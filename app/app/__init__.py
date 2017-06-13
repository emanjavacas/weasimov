import os
import sys

import flask
from flask_login import LoginManager
sys.path.append(os.path.abspath("../generation"))
from Synthesizer import Synthesizer

app = flask.Flask(__name__)
app.config.from_object('config')
app.synthesizer = Synthesizer(model_dir=app.config['MODEL_DIR'])

from app import views
