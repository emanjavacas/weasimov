import flask
from flask_login import LoginManager
from app import Synthesizer

app = flask.Flask(__name__)
app.config.from_object('config')
app.synthesizer = Synthesizer.Synthesizer(model_dir=app.config['MODEL_DIR'])
app.synthesizer.load(model_names=app.config['MODEL_NAMES'])

from app import views
