
# WeAsimov app

## Running the app

## Configuration

``` python
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Model
MODEL_DIR = os.path.join(basedir, 'models')

# Database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'weasimov.db') + '?check_same_thread=False'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# Sentence sampler
FILEDIR = os.path.join(basedir, 'data/novels/')
METAPATH = os.path.join(basedir, 'metainfo.csv')

# Model names
MODEL_NAMES = {
    'fine_asi_giph.LSTM.1l.2048h.64e.256b.pt': 'Isaac Asimov & Ronald Giphart',
    'fine_asi.LSTM.1l.2048h.64e.256b.pt': 'Isaac Asimov',
    'fine_asi_hem.LSTM.1l.2048h.64e.256b.pt': 'Isaac Asimov & Kristien Hemmerechts',
    'MEDIUM.pt': 'Alles'
}

IGNORE_UNNAMED = True  # ignore models if not listed in MODEL_NAMES?

# Defaults
DEFAULTS = {
    "temperature": 0.35,
    "max_seq_len": 100,
    "batch_size": 3,
    "ignore_eos": True,
    "gpu": False
}
```

## Prerequisites

You'll need some package managers.

- `npm`
- `pip`

`npm` typically bundles with `node` itself. To get `node` you would probably like some kind of node version manager like `n` (the only one I've ever used).

## Setup

For the frontend:

If you don't have webpack, install it:

```
npm install -g webpack
```

Then, use `npm` to install the remaining JavaScript dependencies.

```
npm install
```

## Development

The entry point for the app is in `static/components/app.js`.

While developing on the frontend, run `npm run-script run` to keep re-compiling your JavaScript code.

For production run `npm run-script build`, which will create a file in `static/bundle.js`, which is 
the bundled version of the frontend code for production (minified, using production builds of react, etc...).

## Running the app

Before running the Flask app, make sure you have set up the database. If not, simply run:

```make```

in the `weasimov/app` dir.

Run the Flask app

```
python run.py
```
