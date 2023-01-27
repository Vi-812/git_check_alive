import os
from flask import Flask
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.ERROR)

app_flask = Flask(__name__)
app_flask.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
token_flask = os.getenv('TOKEN')
