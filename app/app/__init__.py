import os
from .synthesizer import Synthesizer
from .sentence_sampler import RandomSentenceSampler

import flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_rq2 import RQ

from celery import Celery

app = flask.Flask(
    __name__,
    static_folder='../static',
    template_folder='../templates')

# Configure
app.config.from_object('config.Config')

# Database
db = SQLAlchemy(app)

celery = Celery(
    __name__,
    broker=os.environ.get('CELERY_BROKER_URL', 'redis://'),
    backend=os.environ.get('CELERY_BROKER_URL', 'redis://'))
celery.config_from_object('celeryconfig')


# Login Manager
lm = LoginManager()
lm.session_protection = 'strong'
lm.init_app(app)
lm.login_view = 'register'

# bcrypt
bcrypt = Bcrypt(app)

# mail
mail = Mail(app)

# Services
model_dir = app.config['MODEL_DIR']
gpu = app.config.get('DEFAULTS', {}).get('gpu', False)
sentence_sampler = RandomSentenceSampler(
    app.config['FILEDIR'],
    app.config['METAPATH'])
app.synthesizer = Synthesizer(
    model_dir=model_dir,
    gpu=gpu,
    sentence_sampler=sentence_sampler)

# WebSockets
socketio = SocketIO(app) #  message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'],  async_mode='threading')

from app import views, models
