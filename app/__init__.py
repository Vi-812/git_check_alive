import asyncio
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

# Достаем токен для работы программы через главную страницу (не API)
load_dotenv()
token_flask = os.getenv('TOKEN')

loop = asyncio.get_event_loop()


app_flask = Flask(__name__)
app_flask.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

app_dir = os.path.abspath(os.path.dirname('__init__.py'))
db_dir = os.path.join(app_dir, 'instance')
if not os.path.exists(db_dir):
    os.makedirs(db_dir)
app_flask.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(db_dir, 'repositories.db')
app_flask.config['SQLALCHEMY_MIGRATE_REPO'] = os.path.join(db_dir, 'db_migrate')
db = SQLAlchemy(app_flask)
migrate = Migrate(app_flask, db)

from app import models

with app_flask.app_context():
    db.create_all()
