from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource, marshal
from werkzeug.exceptions import HTTPException, default_exceptions

from app.database import db
from app.endpoints.profiles.resource import ProfileResources
from app.endpoints.projects.model import Project
from app.endpoints.projects.resource import (
    ProjectDataResources,
    ProjectResources,
    ProjectStatusResource,
    project_home_fields,
)
from config import Config

app = Flask(__name__)
CORS(app)
migrate = Migrate()


@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(error=str(e)), code


for ex in default_exceptions:
    app.register_error_handler(ex, handle_error)

app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config["BUNDLE_ERRORS"] = Config.BUNDLE_ERRORS

db.init_app(app)
migrate.init_app(app, db)
api = Api(app)
api.prefix = "/api"

with app.app_context():
    db.create_all()


class HomePage(Resource):
    @staticmethod
    def get():
        projects = Project.query.filter_by(**{}).order_by(Project.name)
        projects = projects.limit(3)
        project = projects.all()
        return marshal(project, project_home_fields)


api.add_resource(HomePage, "/")
api.add_resource(ProjectResources, "/projects", "/projects/<int:project_id>")
api.add_resource(
    ProjectStatusResource, "/projects", "/projects/<int:project_id>/status"
)
api.add_resource(ProjectDataResources, "/data", "/data/<int:sensor_id>")
api.add_resource(ProfileResources, "/profiles", "/profiles/<int:profile_id>")


if __name__ == "__main__":
    app.run(host="localhost", port=5000)
