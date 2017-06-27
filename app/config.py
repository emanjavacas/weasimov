import os
basedir = os.path.abspath(os.path.dirname(__file__))

# model
MODEL_DIR = os.path.join(basedir, 'models')

# database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'weasimov.db') + '?check_same_thread=False'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
