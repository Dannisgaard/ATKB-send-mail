from flask import flash, redirect, url_for
from flask import Blueprint, render_template, request
from app.models import db, Person, Mail, person_identifier

lister_blueprint = Blueprint("lister", __name__)


@lister_blueprint.route("/")
def lister():
    all_persons = Person.query.all()
    return render_template("lister.html", persons=all_persons)


@lister_blueprint.route("/<id>", methods=["POST"])
def update_mailliste_for_person(id):
    error = None
    person_to_update = Person.query.filter_by(person_id=id).first()
    medlem_checked = "medlem" in request.form.getlist("maillist")
    fredagsbar_checked = "fredagsbar" in request.form.getlist("maillist")

    mail_to_update = Mail.query.filter_by(mail_id=1).first()
    if medlem_checked:
        if person_to_update not in mail_to_update.persons:
            mail_to_update.persons.append(person_to_update)

    else:
        if person_to_update in mail_to_update.persons:
            mail_to_update.persons.remove(person_to_update)

    db.session.add(mail_to_update)
    db.session.commit()
    mail_to_update = Mail.query.filter_by(mail_id=3).first()
    if fredagsbar_checked:
        if person_to_update not in mail_to_update.persons:
            mail_to_update.persons.append(person_to_update)
    else:
        if person_to_update in mail_to_update.persons:
            mail_to_update.persons.remove(person_to_update)

    db.session.add(mail_to_update)
    db.session.commit()
    flash(person_to_update.person_fistName + " er nu opdateret!")
    return redirect(url_for("lister.lister"))
