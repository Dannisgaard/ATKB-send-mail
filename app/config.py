import os

print("Read config from .env file")


class Config(object):
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY") or "supersekrit"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///app.sqlite3"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER")
    ALLOWED_EXTENSIONS = os.environ.get("ALLOWED_EXTENSIONS")
    SURESMS_API_PW = os.environ.get("SURESMS_API_PW")
    SMTPHOST = os.environ.get("SMTPHOST")
    SMTPPASS = os.environ.get("SMTPPASS")
    SLEEP = os.environ.get("SLEEP")
    TLS = os.environ.get("TLS")
    ME = os.environ.get("ME")
