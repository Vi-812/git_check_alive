import os
from sanic import Sanic
from sanic_jinja2 import SanicJinja2
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
token_app = os.getenv('TOKEN')

app_sanic = Sanic(name='git_check_alive')
app_sanic.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app_sanic.config.REQUEST_TIMEOUT = 1800
app_sanic.config.RESPONSE_TIMEOUT = 1800

jinja = SanicJinja2(app_sanic, pkg_name='frontend')

APP_DIR = os.path.abspath(os.path.dirname('__init__.py'))
DB_DIR = os.path.join(APP_DIR, 'backend/db')
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

db = create_engine('sqlite:///' + os.path.join(DB_DIR, 'repo.db'), future=True)
from frontend import models
