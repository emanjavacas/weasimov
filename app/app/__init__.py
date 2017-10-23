
from .synthesizer import Synthesizer
from .sentence_sampler import RandomSentenceSampler

import flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt

app = flask.Flask(
    __name__,
    static_folder='../static',
    template_folder='../templates')

# Configure
app.config.from_object('config.Config')

# Database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "=\x07BoZ\xeb\xb0\x13\x88\xf8mW(\x93}\xe6k\r\xebA\xbf\xff\xb1v"
db = SQLAlchemy(app)

# Login Manager
lm = LoginManager()
lm.session_protection = 'strong'
lm.init_app(app)
lm.login_view = 'register'

# bcrypt
bcrypt = Bcrypt(app)

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
socketio = SocketIO(app)

from app import views, models
