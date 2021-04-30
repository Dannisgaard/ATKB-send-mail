from flask import flash
from flask import Blueprint, render_template, request
from app.models import db, Person, Log

home_blueprint = Blueprint("home", __name__)


@home_blueprint.route("/")
def home():
    return render_template("home.html")


@home_blueprint.route("/log")
def log():
    all_logs = Log.query.all()
    return render_template("log.html", logs=all_logs)

