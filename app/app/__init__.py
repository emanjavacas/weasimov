import os
import sys; sys.path.append(os.path.abspath("../generation"))

from Synthesizer import Synthesizer

import flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = flask.Flask(__name__,
                  static_folder='../static',
                  template_folder='../templates')

# Configure
app.config.from_object('config')

# Database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "=\x07BoZ\xeb\xb0\x13\x88\xf8mW(\x93}\xe6k\r\xebA\xbf\xff\xb1v"
db = SQLAlchemy(app)

# login manager
lm = LoginManager()
lm.session_protection = 'strong'
lm.init_app(app)
lm.login_view = 'login'

# Services
app.synthesizer = Synthesizer(model_dir=app.config['MODEL_DIR'])

from app import views, models
