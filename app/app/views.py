import json
import flask
from app import app

@app.route('/')
def index():
    return flask.render_template('index.html')

def generate():
    return 'generated text'

def temperature():
    pass

def select_model():
    pass
