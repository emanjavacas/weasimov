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
    seed = flask.request.json["selection"]
    temperature = float(flask.request.json['temperature'])
    max_seq_len = int(flask.request.json['max_seq_len'])
    if not seed:
        seed = None
    else:
        seed_ends_with_space = seed.endswith(' ')
        seed = [' '.join(nltk.word_tokenize(seed, language="dutch"))]
        if seed_ends_with_space:
            seed[0] += ' '
    try:
        hyps = app.synthesizer.sample(
            model_name=flask.request.json['model_name'],
            seed_texts=seed,
            temperature=temperature,
            ignore_eos=True,
            max_seq_len=max_seq_len,
            batch_size=5,
            max_tries=1)
        return flask.jsonify(status='OK', hyps=hyps)
    except ValueError as e:
        return flask.jsonify(status='Error', message=str(e)), 500

@app.route('/temperature', methods=['POST'])
def temperature():
    app.synthesizer.temperature = float(flask.request.json["data"])
    return flask.jsonify(
        status='OK',
        message=f'temperature adjusted to {app.synthesizer.temperature}',
        temperature=app.synthesizer.temperature)

@app.route('/models', methods=['GET'])
def models():
    return flask.jsonify(status='OK', models=app.synthesizer.list_models())

@app.route('/load_model', methods=['POST'])
def load_model():
    model_name = flask.request.json['model_name']
    app.synthesizer.load(model_names=(model_name,))
    return flask.jsonify(status='OK',
                         model={'path': model_name,
                                'loaded': True})
