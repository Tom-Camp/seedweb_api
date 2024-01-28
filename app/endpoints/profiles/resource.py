import json

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
from app.endpoints.profiles.model import Color, Profile, RgbColor


class ColorField(fields.Raw):
    def format(self, value):
        clr = json.loads(value)
        color_sets: list = []
        for color_id in clr:
            color_list = Color.query.get(color_id)
            color_sets.append((color_list.r, color_list.g, color_list.b))
        return color_sets


colors_fields: dict = {"colors": ColorField()}

profile_fields: dict = {
    "name": fields.String,
    "colors": ColorField(),
}

profile_list_fields: dict = {
    "id": fields.Integer,
    "name": fields.String,
    "colors": fields.List(ColorField()),
}

profile_post_parser = reqparse.RequestParser()
profile_post_parser.add_argument(
    "name",
    type=str,
    required=True,
    location=["json"],
    help="The name parameter is required",
)
profile_post_parser.add_argument("colors")


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

    @marshal_with(profile_fields)
    def post(self) -> Profile:
        args = profile_post_parser.parse_args()
        new_colors = self.add_colors(args=args)
        profile = Profile(
            name=args.get("name"),
            colors=new_colors,
        )

        try:
            db.session.add(profile)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"Error creating Profile: {str(e)}")

        return profile

    @marshal_with(profile_fields)
    def patch(self, profile_id: int):
        args = profile_post_parser.parse_args()
        profile = Profile.query.get_or_404(profile_id)

        if profile:
            if "name" in args:
                profile.name = args.get("name")

            if "colors" in args:
                new_colors = self.add_colors(args)
                profile.colors = new_colors
            db.session.commit()

            return profile, 200
        else:
            return {"message": "Item not found"}, 404

    @staticmethod
    def delete(profile_id: int):
        profile = Profile.query.get_or_404(profile_id)
        db.session.delete(profile)
        db.session.commit()

        return {"message": f"Profile: {profile.name} deleted."}, 204

    @staticmethod
    def add_colors(args: dict) -> str:
        color_list: list = []

        if isinstance(args.get("colors"), str):
            color_json = json.loads(args.get("colors", ""))
            for color in color_json:
                rgb_color = RgbColor(r=color[0], g=color[1], b=color[2])
                color_obj = Color.query.filter_by(color=rgb_color).first()

                if not color_obj:
                    color_obj = Color(color=rgb_color)
                    db.session.add(color_obj)
                    db.session.commit()

                color_list.append(color_obj.id)
        return json.dumps(color_list)
