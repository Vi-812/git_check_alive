import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import views, models
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
app_flask.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(db_dir, 'saved_repositories.db')
app_flask.config['SQLALCHEMY_MIGRATE_REPO'] = os.path.join(db_dir, 'db_repository')
db = SQLAlchemy()
db.init_app(app_flask)

