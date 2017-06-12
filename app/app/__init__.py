import os
import sys

import flask
from flask_login import LoginManager
sys.path.append(os.path.abspath("../generation"))
import Synthesizer

app = flask.Flask(__name__)
app.config.from_object('config')
app.synthesizer = Synthesizer.Synthesizer(model_dir=app.config['MODEL_DIR'])
app.synthesizer.load(model_names=app.config['MODEL_NAMES'])

from app import views
