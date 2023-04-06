import os
from sanic import Sanic
from sanic_jinja2 import SanicJinja2
from sanic_ext import Extend
from sanic_cors import CORS, cross_origin
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
token_app = os.getenv('TOKEN')  # Загрузка токена, используется если пользователь не передал свой

app_sanic = Sanic(name='git_check_alive')  # Создаем экземпляр Sanic
app_sanic.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # SECRET_KEY для работы с формами на сайте
app_sanic.config.REQUEST_TIMEOUT = 1800
app_sanic.config.RESPONSE_TIMEOUT = 1800




cors = CORS(app_sanic, resources={
    r"*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
        "allow_headers": ["content-type", "token"],
    }
})




jinja = SanicJinja2(app_sanic, pkg_name='frontend')  # Создаем экземпляр SanicJinja2

APP_DIR = os.path.abspath(os.path.dirname('__init__.py'))  # Определяем путь приложения
DB_DIR = os.path.join(APP_DIR, 'backend/db')  # Задаем путь для DB
if not os.path.exists(DB_DIR):  # Создаем если не существует
    os.makedirs(DB_DIR)

db = create_engine('sqlite:///' + os.path.join(DB_DIR, 'repo.db'), future=True)  # Создаем экземпляр db
