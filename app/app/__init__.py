import os
import sys; sys.path.append(os.path.abspath("../generation"))

from Synthesizer import Synthesizer

import flask

app = flask.Flask(__name__,
                  static_folder='../static',
                  template_folder='../templates')

# Configure
app.config.from_object('config')

# Services
app.synthesizer = Synthesizer(model_dir=app.config['MODEL_DIR'])

from app import views
