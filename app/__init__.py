import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.ERROR)

app_flask = Flask(__name__)
app_flask.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app_flask.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///saved_repositories.db"
db = SQLAlchemy()
db.init_app(app_flask)
token_flask = os.getenv('TOKEN')



