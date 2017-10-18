
# WeAsimov app

## Running the app

## Configuration

```python
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Model
MODEL_DIR = os.path.join(basedir, 'data/models/')

# Database
if os.environ.get("WEASIMOV_DB_URL") is None:
    print("Falling back to SQLite DB.")
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'weasimov.db') + '?check_same_thread=False'
else:
    print("Using MySQL Database")
    SQLALCHEMY_DATABASE_URI = os.environ['WEASIMOV_DB_URL']
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# Sentence sampler
FILEDIR = os.path.join(basedir, 'data/novels/')
METAPATH = os.path.join(basedir, 'data/metainfo.csv')

# Model names
MODEL_NAMES = {
    'LARGE.pt': 'A. Dante',
    'fine_gip_large.LSTM.1l.4096h.64e.256b.2.40.pt': 'R. Giphart',
    'fine_asi_gip_large.LSTM.1l.4096h.64e.256b.2.26.pt':  'I. Robhart',
    'fine_asi_hem_large.LSTM.1l.4096h.64e.256b.2.51.pt': 'K. Hembot',
    'fine_asi_reve.LSTM.1l.4096h.64e.256b.2.17.pt': 'G. Revimov',
    'fine_asi_nes_large.LSTM.1l.4096h.64e.256b.2.14.pt': 'I. Nescimov',
    'fine_asi.LSTM.1l.2048h.64e.256b.2.31.pt': 'I. Asimov',
    'fine_robot_large.LSTM.1l.4096h.64e.256b.1.87.pt': 'Robot Ik'
}

# Defaults
DEFAULTS = {
    "temperature": 0.35,
    "max_seq_len": 100,
    "batch_size": 3,
    "ignore_eos": True,
    "gpu": False
}

IGNORE_UNNAMED = True  # ignore models if not listed in MODEL_NAMES?
MONITORS = ['admin']
```

## Database

The app can be run with either SQLite or MySQL. To work with MySQL, a number of variables need to be in place. First create a database in MySQL, e.g.:

```sql
create database weasimov character set utf8 collate utf8_bin;
```

It might also be convenient to create a new user and grant all privileges to that user:

```sql
create user 'weasimov'@'localhost' identified by 'password';
grant all privileges on weasimov.* to 'weasimov'@'localhost';
flush privileges;
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

Before running the Flask app, make sure you have set up the database. If not, and you want to use SQLite, run:

```make```

in the `weasimov/app` dir. For MySQL, run something like

```bash
WEASIMOV_DB_URL=mysql+mysqldb://weasimov:weasimov@localhost/weasimov
```

Run the Flask app as follows with a SQLite DB:

```
python run.py --port 5555 --host localhost
```

and like this with MySQL:

```
WEASIMOV_DB_URL=mysql+mysqldb://weasimov:weasimov@localhost/weasimov python run.py --port 5555 --host localhost
```
