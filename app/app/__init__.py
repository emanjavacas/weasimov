import flask
from flask_login import LoginManager

app = flask.Flask(__name__)
# app.config.from_object('config')

from app import views
