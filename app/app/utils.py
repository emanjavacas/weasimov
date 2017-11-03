import itsdangerous
import flask_mail

from app import app, mail, celery


ts = itsdangerous.URLSafeTimedSerializer(app.config["SECRET_KEY"])

def send_email(recipient, subject, html):
    msg = flask_mail.Message(
        subject,
        sender=app.config['MAIL_USERNAME'],
        recipients=[recipient])
    msg.html = html
    send_async_mail.apply_async(args=(msg), queue='mail-queue')

@celery.task
def send_async_mail(msg):
    with app.app_context():
        mail.send(msg)
