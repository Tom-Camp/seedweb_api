import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URI"
    ) or "sqlite:///" + os.path.join(basedir, "instance", "seedy.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BUNDLE_ERRORS = True
