import json
import flask
from app import app

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/savechange', methods=['POST'])
def savechange():
    data = flask.request.json
    print(data)
    return flask.jsonify(status='OK', message='changes saved.')

@app.route('/savedoc', methods=['POST'])
def savedoc():
    data = flask.request.json
    print(data)
    return flask.jsonify(status='OK', message='document saved.')


def generate():
    return 'generated text'

def temperature():
    pass

def select_model():
    pass
