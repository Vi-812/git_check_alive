import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func
from dotenv import load_dotenv
import logging

# Достаем токен для работы программы через главную страницу (не API)
load_dotenv()
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.ERROR)
token_flask = os.getenv('TOKEN')

app_flask = Flask(__name__)
app_flask.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db_dir = os.path.abspath(os.path.dirname('__init__.py')) + r'\instance'
if not os.path.exists(db_dir):
    os.makedirs(db_dir)
app_flask.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(db_dir, 'repositories.db')
app_flask.config['SQLALCHEMY_MIGRATE_REPO'] = os.path.join(db_dir, 'db_migrate')
db = SQLAlchemy(app_flask)
migrate = Migrate(app_flask, db)

from app import models, database

with app_flask.app_context():
    db.create_all()
