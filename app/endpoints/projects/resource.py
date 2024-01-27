import json
from datetime import datetime

from flask_restful import Resource, fields, marshal, marshal_with, reqparse, request

from app import db
from app.endpoints.projects.model import Project, ProjectData, ProjectNotes


class SensorDataJson(fields.Raw):
    def format(self, value):
        return json.loads(value)


class FormatDate(fields.Raw):
    def format(self, value):
        return value.strftime("%b %d, %Y - %H:%M")


sensor_fields: dict = {
    "sensor_data": SensorDataJson(),
    "created_date": FormatDate(),
}


note_fields: dict = {
    "note": fields.String,
    "created_date": FormatDate(),
}

project_fields: dict = {
    "name": fields.String,
    "bed_id": fields.String,
    "description": fields.String,
    "profile": fields.String,
    "start": fields.String,
    "end": fields.String,
    "data": fields.List(fields.Nested(sensor_fields)),
    "notes": fields.List(fields.Nested(note_fields)),
}

project_list_fields: dict = {
    "id": fields.Integer,
    "updated": fields.DateTime,
    "name": fields.String,
    "bed_id": fields.String,
    "profile": fields.String,
}

project_home_fields: dict = {
    "id": fields.Integer,
    "updated": FormatDate(),
    "name": fields.String,
    "bed_id": fields.String,
    "data": fields.List(fields.Nested(sensor_fields)),
}

project_post_parser = reqparse.RequestParser()
project_post_parser.add_argument(
    "name",
    type=str,
    required=True,
    location=["json"],
    help="The name parameter is required",
)
project_post_parser.add_argument(
    "bed_id",
    type=str,
    required=True,
    location=["json"],
    help="The bed_id parameter is required",
)
project_post_parser.add_argument(
    "description",
    type=str,
    required=True,
    location=["json"],
    help="The description parameter is required",
)
project_post_parser.add_argument("profile_id")
project_post_parser.add_argument("start")
project_post_parser.add_argument("end")


class ProjectResources(Resource):
    @staticmethod
    def get(project_id=None) -> dict:
        if project_id:
            project = Project.query.get_or_404(project_id)
            return marshal(project, project_fields)
        else:
            args = request.args.to_dict()
            limit = args.get("limit", 0)
            offset = args.get("offset", 0)

            args.pop("limit", None)
            args.pop("offset", None)

            projects = Project.query.filter_by(**args).order_by(Project.name)

            if limit:
                projects = projects.limit(limit)

            if offset:
                projects = projects.offset(offset)

            project = projects.all()

            return marshal(project, project_list_fields)

    @staticmethod
    @marshal_with(project_fields)
    def post() -> Project:
        args = project_post_parser.parse_args()

        project = Project(**args)
        db.session.add(project)
        db.session.commit()

        return project

    @staticmethod
    def patch(project_id: int):
        args = project_post_parser.parse_args()
        project = Project.query.get_or_404(project_id)

        if project:
            if "name" in args:
                project.name = args.get("name")

            if "bed_id" in args:
                project.bed_id = args.get("bed_id")

            if "description" in args:
                project.description = args.get("description")

            if "start" in args:
                project.start = args.get("start")

            if "end" in args:
                project.end = args.get("end")

            if "profile_id" in args:
                project.profile_id = args.get("profile_id")

            db.session.commit()
            return {"message": "Item updated successfully"}, 200
        else:
            return {"message": "Item not found"}, 404

    @staticmethod
    def delete(project_id):
        project = Project.query.get_or_404(project_id)

        db.session.delete(project)
        db.session.commit()

        return "", 204


class ProjectStatusResource(Resource):
    @staticmethod
    def get(project_id=None) -> dict:
        project = Project.query.get_or_404(project_id)
        now = datetime.now()
        base = datetime.now().strftime("%m/%d/%y")
        start = datetime.strptime(f"{base} {project.start}", "%m/%d/%y %H:%M")
        end = datetime.strptime(f"{base} {project.end}", "%m/%d/%y %H:%M")
        status = True if now > start and now < end else False
        return {"status": status, "profile": project.profile}


sensor_post_parser = reqparse.RequestParser()
sensor_post_parser.add_argument(
    "sensor_data",
    type=str,
    required=True,
    location=["json"],
    help="The sensor_data parameter is required",
)
sensor_post_parser.add_argument(
    "project_id",
    type=str,
    required=True,
    location=["json"],
    help="The project_id parameter is required",
)


class ProjectDataResources(Resource):
    @staticmethod
    def get(sensor_id: int):
        sensor_data = ProjectData.query.get_or_404(sensor_id)
        return marshal(sensor_data, sensor_fields)

    @staticmethod
    @marshal_with(sensor_fields)
    def post() -> ProjectData:
        args = sensor_post_parser.parse_args()

        sensor = ProjectData(**args)
        db.session.add(sensor)
        db.session.commit()
        return sensor

    @staticmethod
    def patch(sensor_id: int):
        args = project_post_parser.parse_args()
        sensor_data = ProjectData.query.get_or_404(sensor_id)

        if sensor_data:
            if "sensor_data" in args:
                sensor_data.name = args.get("sensor_data")
            return {"message": "Item updated successfully"}, 200
        else:
            return {"message": "Item not found"}, 404

    @staticmethod
    def delete(sensor_id: int):
        sensor_data = ProjectData.query.get_or_404(sensor_id)

        db.session.delete(sensor_data)
        db.session.commit()

        return "", 204


notes_post_parser = reqparse.RequestParser()
notes_post_parser.add_argument(
    "note",
    type=str,
    required=True,
    location=["json"],
    help="The note parameter is required",
)
notes_post_parser.add_argument(
    "project_id",
    type=str,
    required=True,
    location=["json"],
    help="The project_id parameter is required",
)


class ProjectNoteResources(Resource):
    @staticmethod
    def get(note_id: int):
        note = ProjectNotes.query.get_or_404(note_id)
        return marshal(note, note_fields)

    @staticmethod
    @marshal_with(note_fields)
    def post() -> ProjectNotes:
        args = notes_post_parser.parse_args()

        note = ProjectNotes(**args)
        db.session.add(note)
        db.session.commit()
        return note

    @staticmethod
    def patch(note_id: int):
        args = notes_post_parser.parse_args()
        note_obj = ProjectNotes.query.get_or_404(note_id)

        if note_obj:
            if "note" in args:
                note_obj.note = args.get("note")
            return {"message": "Note updated successfully"}, 200
        else:
            return {"message": "Note not found"}, 404

    @staticmethod
    def delete(note_id: int):
        note_obj = ProjectData.query.get_or_404(note_id)

        db.session.delete(note_obj)
        db.session.commit()

        return "The note was deleted", 204
