# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import requests
import json
from flask import Blueprint, render_template, request
from flask import flash, redirect, url_for, send_from_directory
from flask import jsonify, current_app
from app.models import db, Person, SmsTextMessage, MailTextMessage, Mail, Log
import threading
from flask import current_app as app
from werkzeug.utils import secure_filename
import time
from datetime import datetime as datetime1
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from email import encoders
from email.mime.base import MIMEBase
import smtplib
import datetime


mail_blueprint = Blueprint("mail", __name__)
maillogtext_list = []
path_and_filename = ""
filename = ""
subject = ""


@mail_blueprint.route("/")
def home():
    return render_template("mail.html")


@mail_blueprint.route("/fredagsbar", methods=["GET", "POST"])
def fredagsbar():
    mailtype_fredagsbar = Mail.query.filter_by(mail_id=3).first()
    mailtext = (
        MailTextMessage.query.filter_by(
            mailtextmessage_id=mailtype_fredagsbar.mailTextmessage_id
        )
        .first()
        .text
    )
    smstype_fredagsbar = Mail.query.filter_by(mail_id=1).first()
    smstext = (
        SmsTextMessage.query.filter_by(
            smstextmessage_id=smstype_fredagsbar.smsTextmessage_id
        )
        .first()
        .text
    )
    mailsenddate = time.strftime("%d-%m-%Y %H:%M")
    today = datetime1.today()
    friday = today + datetime.timedelta((4 - today.weekday()) % 7)
    friday_six_oclock = friday.replace(hour=6, minute=0)
    smssenddate = friday_six_oclock.strftime("%d-%m-%Y %H:%M")
    if request.method == "POST":
        all_fredagsbar = Person.query.filter(
            Person.mailslists.any(mail_name="fredagsbar")
        ).all()
        thread = threading.Thread(
            target=fredagsbar_worker,
            args=(
                mailtext,
                smstext,
                all_fredagsbar,
                db,
                current_app._get_current_object(),
                friday_six_oclock,
            ),
        )
        thread.start()
        return render_template("fredagsbarSending.html")

    return render_template(
        "fredagsbar.html",
        mailtext=mailtext,
        smstext=smstext,
        smssenddate=smssenddate,
        mailsenddate=mailsenddate,
    )


@mail_blueprint.route("/medlemmerpdf", methods=["GET", "POST"])
def medlemmerPDF():
    if request.method == "POST":
        global path_and_filename
        global filename
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == "":
            flash("Der er ikke valgt en fil!")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path_and_filename = os.path.join(
                app.root_path, app.config["UPLOAD_FOLDER"], filename
            )
            file.save(path_and_filename)

            mailtype_medlem = Mail.query.filter_by(mail_id=1).first()
            mailtext = (
                MailTextMessage.query.filter_by(
                    mailtextmessage_id=mailtype_medlem.mailTextmessage_id
                )
                .first()
                .text
            )

            return render_template(
                "medlemmerPdf.html", filename=filename, mailtext=mailtext
            )
    return render_template("medlemmerPdf.html")


@mail_blueprint.route("/medlemmer", methods=["GET", "POST"])
def medlemmer():
    if request.method == "GET":
        
        mailtype_medlem = Mail.query.filter_by(mail_id=1).first()
        mailtext = (
            MailTextMessage.query.filter_by(
                mailtextmessage_id=mailtype_medlem.mailTextmessage_id
            )
            .first()
            .text
        )

        return render_template(
            "medlemmer.html", mailtext=mailtext
        )
    return render_template("medlemmer.html")


@mail_blueprint.route("/fredagsbartekster")
def fredagsbartekster():
    all_mailtexts = MailTextMessage.query.all()
    all_smstexts = SmsTextMessage.query.all()

    return render_template(
        "fredagsbartekster.html",
        sms_text_messages=all_smstexts,
        mail_text_messages=all_mailtexts,
    )


@mail_blueprint.route("/medlemstekster")
def medlemstekster():
    all_mailtexts = MailTextMessage.query.all()
    all_smstexts = SmsTextMessage.query.all()

    return render_template(
        "medlemstekster.html",
        sms_text_messages=all_smstexts,
        mail_text_messages=all_mailtexts,
    )


@mail_blueprint.route("/oprettekster")
def opret_tekster():
    return render_template("opret-tekster.html")


@mail_blueprint.route("/oprettekster/smstext", methods=["POST"])
def create_smstext():
    name = request.form["tekstName"]
    text = request.form["smstext"]

    newtext = SmsTextMessage(name=name, text=text)
    db.session.add(newtext)
    db.session.commit()
    flash("SMS tekst er nu oprettet!")
    return redirect(url_for("mail.opret_tekster"))


@mail_blueprint.route("/oprettekster/mailtext", methods=["POST"])
def create_mailtext():
    name = request.form["tekstName"]
    text = request.form["mailtext"]

    newtext = MailTextMessage(name=name, text=text)
    db.session.add(newtext)
    db.session.commit()
    flash("Mail tekst er nu oprettet!")
    return redirect(url_for("mail.opret_tekster"))


@mail_blueprint.route("/getfredagsbarmailtext/<id>")
def getfredagsbarmailtext(id):
    # save selecte text in DB
    mailtype = Mail.query.filter_by(mail_id=3).first()
    mailtype.mailTextmessage_id = id
    db.session.commit()
    return MailTextMessage.query.filter_by(mailtextmessage_id=id).first().text


@mail_blueprint.route("/getfredagsbarsmstext/<id>")
def getfredagsbarsmstext(id):
    # save selecte text in DB
    mailtype = Mail.query.filter_by(mail_id=3).first()
    mailtype.smsTextmessage_id = id
    db.session.commit()
    return SmsTextMessage.query.filter_by(smstextmessage_id=id).first().text


@mail_blueprint.route("/getmedlemsmailtext/<id>")
def getmedlemsmailtext(id):
    # save selecte text in DB
    mailtype = Mail.query.filter_by(mail_id=1).first()
    mailtype.mailTextmessage_id = id
    db.session.commit()
    return MailTextMessage.query.filter_by(mailtextmessage_id=id).first().text


@mail_blueprint.route("/getmedlemssmstext/<id>")
def getmedlemssmstext(id):
    # save selecte text in DB
    mailtype = Mail.query.filter_by(mail_id=1).first()
    mailtype.smsTextmessage_id = id
    db.session.commit()
    return SmsTextMessage.query.filter_by(smstextmessage_id=id).first().text


@mail_blueprint.route("/edittext/mailtext", methods=["POST"])
def edit_mailtext():
    text = request.form["mailtext"]
    textName = request.form["medlemsmailtekster"]

    mailtype = Mail.query.filter_by(mail_id=3).first()
    text_id = mailtype.mailTextmessage_id
    newtext = MailTextMessage.query.filter_by(name=textName).first()

    newtext.text = text
    db.session.commit()
    flash("Mail tekst er nu opdateret!")
    return redirect(url_for("home.home"))


@mail_blueprint.route("/edittext/smstext", methods=["POST"])
def edit_smstext():
    text = request.form["smstext"]
    textName = request.form["medlemssmstekster"]

    mailtype = Mail.query.filter_by(mail_id=3).first()
    text_id = mailtype.smsTextmessage_id
    newtext = SmsTextMessage.query.filter_by(name=textName).first()

    newtext.text = text
    db.session.commit()
    flash("SMS tekst er nu opdateret!")
    return redirect(url_for("home.home"))


def allowed_file(filename):
    ALLOWED_EXTENSIONS = app.config["ALLOWED_EXTENSIONS"]
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@mail_blueprint.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@mail_blueprint.route("/sendmail/medlemmer", methods=["POST"])
def sendmail_medlemmer():
    global subject
    subject = request.form["subject"]
    if subject != "":
        flash("Der sendes nu mail til medlemmerne!")
        return redirect(url_for("mail.medlemmer_sending"))
    flash("Udfyld venligst emnefelt!")
    return redirect(url_for("mail.medlemmer"))


@mail_blueprint.route("/medlemmersending")
def medlemmer_sending():
    mailtype_medlem = Mail.query.filter_by(mail_id=1).first()
    mailtext = (
        MailTextMessage.query.filter_by(
            mailtextmessage_id=mailtype_medlem.mailTextmessage_id
        )
        .first()
        .text
    )
    all_members = Person.query.filter(Person.mailslists.any(mail_name="medlem")).all()
    thread = threading.Thread(
        target=members_worker,
        args=(mailtext, all_members, db, current_app._get_current_object()),
    )
    thread.start()
    return render_template("medlemmerSending.html")


def members_worker(mailtext, all_members, db, app):
    print("Starter mail udsendelse\n")
    del maillogtext_list[:]
    today = datetime1.now()
    COMMASPACE = ", "
    me = app.config["ME"]
    time_str = time.strftime("%Y-%m-%d %H:%M:%S")

    with app.app_context():
        for member in all_members:
            if member.person_email is not None and member.person_email != "":
                print(member.person_email)
                print(member.person_fistName)
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = formataddr(
                    ("Allerup Thorup -kultur og beboerforening", me)
                )
                msg["To"] = member.person_email
                msg["Date"] = today.isoformat()
                msg["Message-id"] = today.isoformat() + "@dannisgaard.dk"

                # Create the body of the message (a plain-text and an HTML version).
                text = mailtext.replace("##navn##", member.person_fistName)
                html = (
                    """
                <html>
                <body >
                <font face="verdana">
                    <p> """
                    + mailtext.replace("##navn##", member.person_fistName).replace(
                        "\n", "<br/>"
                    )
                    + """</p>
                </font>   
                </body>
                </html>
                """
                )
                # Record the MIME types of both parts - text/plain and text/html.
                part1 = MIMEText(text, "plain", "utf-8")
                part2 = MIMEText(html, "html", "utf-8")

                # Attach parts into message container.
                # According to RFC 2046, the last part of a multipart message, in this case
                # the HTML message, is best and preferred.
                msg.attach(part1)
                msg.attach(part2)

                if path_and_filename  != '':
                    # Open PDF file in binary mode
                    with open(path_and_filename, "rb") as attachment:
                        # Add file as application/octet-stream
                        # Email client can usually download this automatically as attachment
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())

                    # Encode file in ASCII characters to send by email
                    encoders.encode_base64(part)

                    # Add header as key/value pair to attachment part
                    part.add_header(
                        "Content-Disposition", "attachment; filename=" + filename
                    )

                    # You can start a local SMTP debugging server
                    # python -m smtpd -c DebuggingServer -n localhost:1025
                    msg.attach(part)

                if app.config["SMTPHOST"]:
                    s = smtplib.SMTP(app.config["SMTPHOST"])
                    s.ehlo()
                    if app.config["TLS"] == "True":
                        s.starttls()
                        s.login("lars@dannisgaard.dk", app.config["SMTPPASS"])

                    s.sendmail(me, member.person_email, msg.as_string())

                maillogtext_list.append(
                    {
                        "time": time_str,
                        "sendto": member.person_fistName,
                        "email_adr": member.person_email,
                    }
                )
                message = (
                    "Sendt mail til: "
                    + member.person_fistName
                    + " ("
                    + member.person_email
                    + ")"
                )
                newlog = Log(time=time_str, message=message)
                db.session.add(newlog)
                db.session.commit()
                time.sleep(float(app.config["SLEEP"]))

    maillogtext_list.append(
        {
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "sendto": "Mailudsendelse er færdig!",
            "email_adr": "",
        }
    )


def fredagsbar_worker(mailtext, smstext, all_fredagsbar_member, db, app, friday_date):
    print("Starter mail udsendelse\n")
    # sms auth
    auth_headers = {"Accept": "application/json"}
    auth_payload = "grant_type=password&username=Allerup&password=B7Em4cy6"

    r = requests.post(
        "https://api.suresms.com/json/token", data=auth_payload, headers=auth_headers
    )
    auth_response = json.loads(r.text)
    print(auth_response)
    time.sleep(1)
    # ---------
    del maillogtext_list[:]
    today = datetime1.now()
    COMMASPACE = ", "
    me = app.config["ME"]
    time_str = time.strftime("%Y-%m-%d %H:%M:%S")

    with app.app_context():
        for member in all_fredagsbar_member:
            if member.person_email is not None and member.person_email != "":
                msg = MIMEMultipart("alternative")
                msg["Subject"] = "Fredagsbar i Allerup Forsamlingshus"
                msg["From"] = formataddr(
                    ("Allerup Thorup -kultur og beboerforening", me)
                )
                msg["To"] = member.person_email
                msg["Date"] = today.isoformat()
                msg["Message-id"] = today.isoformat() + "@dannisgaard.dk"

                # Create the body of the message (a plain-text and an HTML version).

                text = mailtext.replace("##dato##", friday_date.strftime("%d-%m-%Y"), 1).replace("##navn##", member.person_fistName)
                html = (
                    """
                <html>
                <body >
                <h2><font face="verdana" size="5">Fredagsbar på fredag i Allerup Forsamlingshus</font></h2>
                <font face="verdana">
                    <p> """
                    + mailtext.replace("##dato##", friday_date.strftime("%d-%m-%Y"), 1)
                    .replace("##navn##", member.person_fistName)
                    .replace("\n", "<br/>")
                    + """</p>
                </font>
                <img src="http://resurser.dannisgaard.dk/images/fredagsbar-skilt.jpg" width="780" height="709" border="0"/>  
                </body>
                </html>
                """
                )
                # Record the MIME types of both parts - text/plain and text/html.
                part1 = MIMEText(text, "plain", "utf-8")
                part2 = MIMEText(html, "html", "utf-8")

                # Attach parts into message container.
                # According to RFC 2046, the last part of a multipart message, in this case
                # the HTML message, is best and preferred.
                msg.attach(part1)
                msg.attach(part2)

                # python -m smtpd -c DebuggingServer -n localhost:1025 for test
                if app.config["SMTPHOST"]:
                    s = smtplib.SMTP(app.config["SMTPHOST"])
                    s.ehlo()
                    if app.config["TLS"] == "True":
                        s.starttls()
                        s.login("lars@dannisgaard.dk", app.config["SMTPPASS"])

                    s.sendmail(me, member.person_email, msg.as_string())

                maillogtext_list.append(
                    {
                        "time": time_str,
                        "sendto": member.person_fistName,
                        "email_adr": member.person_email,
                    }
                )
                message = (
                    "Sendt mail til: "
                    + member.person_fistName
                    + " ("
                    + member.person_email
                    + ")"
                )
                newlog = Log(time=time_str, message=message)
                db.session.add(newlog)
                db.session.commit()

            if member.person_phone is not None:
                # send sms
                payload = {
                    "MessageID": "etId",
                    "MessageText": smstext.replace(
                        "##dato##", friday_date.strftime("%d-%m-%Y"), 1
                    ).replace("##navn##", member.person_fistName),
                    "ToPhoneNumbers": member.person_phone,
                    "SenderID": "Allerup Bar",
                    "SendAsFlash": False,
                    "HasCallBackURL": "",
                    "RequiredDeliveryUTCDateTime": friday_date.isoformat(),
                    "ScheduleDaily": False,
                    "ScheduleDailyExceptWeekend": False,
                    "ScheduleWeekly": False,
                    "ScheduleMonthly": False,
                    "ScheduleYearly": False,
                }

                if "access_token" in auth_response.keys():
                    headers = {
                        "Authorization": "Bearer " + str(auth_response["access_token"])
                    }

                    r = requests.post(
                        "https://api.suresms.com/json/api/Message",
                        data=payload,
                        headers=headers,
                    )
                    message = (
                        "Sendt sms til: "
                        + member.person_fistName
                        + " ("
                        + member.person_phone
                        + ")"
                    )
                    newsmslog = Log(time=time_str, message=message)
                    db.session.add(newsmslog)
                    db.session.commit()

            time.sleep(float(app.config["SLEEP"]))

    maillogtext_list.append(
        {
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "sendto": "Mailudsendelse er færdig!",
            "email_adr": "",
        }
    )


@mail_blueprint.route("/sendmaillogtext")
def sendmaillogtext():
    d = send_mail()
    return jsonify(d)


def send_mail():
    return maillogtext_list
