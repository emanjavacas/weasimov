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
    # TODO: actually save the changes
    return flask.jsonify(status='OK', message='changes saved.')

@app.route('/savedoc', methods=['POST'])
def savedoc():
    data = flask.request.json
    print(data)
    # TODO: actually save the document
    return flask.jsonify(status='OK', message='document saved.')

@app.route('/generate', methods=['POST'])
def generate():
    # TODO: retrieve data from synthesizer
    return flask.jsonify(status='OK', message='generated text')

@app.route('/temperature', methods=['POST'])
def temperature():
    # TODO: actually set the temperature
    return flask.jsonify(status='OK', message=f'temperature adjusted to {flask.request.json["data"]}')

def select_model():
    pass
