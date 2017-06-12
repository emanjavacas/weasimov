import json
import unicodedata
import flask
import nltk
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
    seed = flask.request.json["selection"].strip()
    if not seed:
        seed = None
    else:
        seed = [' '.join(nltk.word_tokenize(seed, language="dutch"))]
    text = app.synthesizer.sample(model_name='char.LSTM.1l.2546h.46e.200b.2.49.pt.cpu.pt',
                           seed_texts=seed,
                           temperature=app.synthesizer.temperature,
                           ignore_eos=True,
                           max_seq_len=200,
                           max_tries=1)
    text = ' '.join(text).replace('\n', ' ')
    return flask.jsonify(status='OK', message=text)

@app.route('/temperature', methods=['POST'])
def temperature():
    app.synthesizer.temperature = float(flask.request.json["data"])
    return flask.jsonify(status='OK', message=f'temperature adjusted to {app.synthesizer.temperature}')

def select_model():
    pass
