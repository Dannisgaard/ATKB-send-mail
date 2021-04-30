from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, ForeignKey
from flask_login import LoginManager, UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from sqlalchemy.orm import sessionmaker, relationship


db = SQLAlchemy()

person_identifier = db.Table(
    "person_identifier",
    db.Column("mail_id", db.Integer, db.ForeignKey("mailtypes.mail_id")),
    db.Column("person_id", db.Integer, db.ForeignKey("persons.person_id")),
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(125), unique=True)
    given_name = db.Column(db.String(35))
    family_name = db.Column(db.String(25))

    def __repr__(self):
        return "<User {} {}>".format(self.given_name, self.family_name)


class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(125), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User)


class Person(db.Model):
    __tablename__ = "persons"
    person_id = db.Column(db.Integer, primary_key=True)
    person_fistName = db.Column(db.String(64))
    person_lastName = db.Column(db.String(64))
    person_email = db.Column(db.String(100), unique=True)
    person_phone = db.Column(db.String(20), unique=True)
    mailslists = relationship("Mail", secondary=person_identifier, back_populates="persons")

    def __repr__(self):
        return "<Person {} {}>".format(self.person_fistName, self.person_lastName)


class MailTextMessage(db.Model):
    __tablename__ = "mailtextmessages"
    mailtextmessage_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    text = db.Column(db.Text)


class SmsTextMessage(db.Model):
    __tablename__ = "smstextmessages"
    smstextmessage_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    text = db.Column(db.Text)


class Mail(db.Model):
    __tablename__ = "mailtypes"
    mail_id = db.Column(db.Integer, primary_key=True)
    mail_name = db.Column(db.String(128), unique=True)
    persons = db.relationship("Person", secondary=person_identifier, back_populates="mailslists")
    mailTextMessage = relationship(MailTextMessage, uselist=False)
    mailTextmessage_id = Column(Integer, ForeignKey(MailTextMessage.mailtextmessage_id))
    smsTextMessage = relationship(SmsTextMessage, uselist=False)
    smsTextmessage_id = Column(Integer, ForeignKey(SmsTextMessage.smstextmessage_id))

    def __repr__(self):
        return "<Maillist {}>".format(self.mail_name)


class Log(db.Model):
    __tablename__ = "logs"
    log_id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    message = db.Column(db.String(80))

    def __repr__(self):
        return "<Time {}>".format(self.time)


# setup login manager
login_manager = LoginManager()
login_manager.login_view = "google.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
