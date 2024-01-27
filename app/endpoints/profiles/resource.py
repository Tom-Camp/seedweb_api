from flask_restful import (
    Resource,
    abort,
    fields,
    marshal,
    marshal_with,
    reqparse,
    request,
)

from app import db
from app.endpoints.profiles.model import Color, ColorAssociation, Profile, RgbColor


class ColorField(fields.Raw):
    def format(self, value):
        return value.r, value.g, value.b


colors: dict = {"color": ColorField()}

profile_fields: dict = {
    "name": fields.String,
    "colors": fields.List(fields.Nested(colors)),
}

profile_list_fields: dict = {
    "id": fields.Integer,
    "name": fields.String,
    "colors": fields.List(fields.Nested(colors)),
}

profile_post_parser = reqparse.RequestParser()
profile_post_parser.add_argument(
    "name",
    type=str,
    required=True,
    location=["json"],
    help="The name parameter is required",
)
profile_post_parser.add_argument(
    "colors",
    type=list,
    required=True,
    location=["json"],
    help="The colors list is required",
)


class ProfileResources(Resource):
    @staticmethod
    def get(profile_id=None) -> dict:
        if profile_id:
            project = Profile.query.get_or_404(profile_id)
            return marshal(project, profile_fields)
        else:
            args = request.args.to_dict()
            limit = args.get("limit", 0)
            offset = args.get("offset", 0)

            args.pop("limit", None)
            args.pop("offset", None)

            profiles = Profile.query.filter_by(**args).order_by(Profile.name)

            if limit:
                profiles = profiles.limit(limit)

            if offset:
                profiles = profiles.offset(offset)

            profile = profiles.all()

            return marshal(profile, profile_list_fields)

    @staticmethod
    @marshal_with(profile_fields)
    def post() -> Profile:
        args = profile_post_parser.parse_args()
        profile = Profile(name=args.get("name"))

        try:
            db.session.add(profile)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"Error creating Profile: {str(e)}")

        for color in args.get("colors"):
            rgb_color = RgbColor(r=color[0], g=color[1], b=color[2])
            color_obj = Color.query.filter_by(color=rgb_color).first()

            if not color_obj:
                color_obj = Color(color=rgb_color)

            try:
                db.session.add(color_obj)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                abort(500, message=f"Error creating Profile: {str(e)}")

            new_assoc = ColorAssociation(
                profile_id=profile.id,
                color_id=color_obj.id,
            )
            try:
                db.session.add(new_assoc)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                abort(500, message=f"Error creating Profile: {str(e)}")

        return profile

    @staticmethod
    def patch(profile_id: int):
        args = profile_post_parser.parse_args()
        profile = Profile.query.get_or_404(profile_id)

        if profile:
            if "name" in args:
                profile.name = args.get("name")

            db.session.commit()
            return {"message": "Profile updated successfully"}, 200
        else:
            return {"message": "Item not found"}, 404

    @staticmethod
    def delete(profile_id):
        project = Profile.query.get_or_404(profile_id)

        db.session.delete(project)
        db.session.commit()

        return "", 204
