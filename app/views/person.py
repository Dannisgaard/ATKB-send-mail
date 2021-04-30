from flask import flash, redirect, url_for
from flask import Blueprint, render_template, request
from app.models import db, Person

person_blueprint = Blueprint("person", __name__)


@person_blueprint.route("/", methods=["GET"])
def person():
    all_persons = Person.query.all()
    return render_template("person.html", persons=all_persons)


@person_blueprint.route("/", methods=["POST"])
def createPerson():
    error = None

    first_name = request.form["firstName"]
    last_name = request.form["lastName"]
    email = request.form["email"]
    phone = request.form["phone"]
    if email == u"":
        email = None
    if phone == u"":
        phone = None
    if first_name is None:
        first_name = " "
    if phone and len(phone) == 8:
        phone = "45" + phone
    if phone and len(phone) < 8:
        flash("Fejl i telefonnummer!")
        return redirect(url_for("person.person"))

    newPerson = Person(
        person_fistName=first_name,
        person_lastName=last_name,
        person_email=email,
        person_phone=phone,
    )
    db.session.add(newPerson)
    db.session.commit()
    flash("Personen " + first_name + " er nu oprettet!")
    all_persons = Person.query.all()
    return render_template("person.html", persons=all_persons)


@person_blueprint.route("/<id>", methods=["POST"])
def deletePerson(id):
    error = None
    person_to_delete = Person.query.filter_by(person_id=id).first()
    if person_to_delete is not None:
        db.session.delete(person_to_delete)
        db.session.commit()
        flash("Personen " + person_to_delete.person_fistName + " er nu slettet!")
    all_persons = Person.query.all()
    return render_template("person.html", persons=all_persons)
