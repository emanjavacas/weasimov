import os
import sys; sys.path.append(os.path.abspath("../generation"))

from Synthesizer import Synthesizer

import flask
from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__,
                  static_folder='../static',
                  template_folder='../templates')

# Configure
app.config.from_object('config')

# Database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "=\x07BoZ\xeb\xb0\x13\x88\xf8mW(\x93}\xe6k\r\xebA\xbf\xff\xb1v"
db = SQLAlchemy(app)

# Services
app.synthesizer = Synthesizer(model_dir=app.config['MODEL_DIR'])

from app import views
