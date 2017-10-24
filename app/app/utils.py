import itsdangerous
import flask_mail

from app import app, mail


ts = itsdangerous.URLSafeTimedSerializer(app.config["SECRET_KEY"])


def send_email(recipient, subject, html):
    msg = flask_mail.Message(
        subject,
        sender=app.config['MAIL_USERNAME'],
        recipients=[recipient])
    msg.html = html
    mail.send(msg)