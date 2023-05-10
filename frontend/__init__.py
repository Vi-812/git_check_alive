from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

import os
from dotenv import load_dotenv




from sanic import Sanic
from sanic_jinja2 import SanicJinja2
from sanic_ext import Extend
from sanic_cors import CORS, cross_origin
from sqlalchemy import create_engine


load_dotenv()
token_app = os.getenv('TOKEN')  # Загрузка токена, используется если пользователь не передал свой

app = FastAPI(timeout=1800, keep_alive=1800)  # Создаем экземпляр FastAPI, задаем таймауты
app.secret_key = os.getenv('SECRET_KEY')  # SECRET_KEY для работы с формами на сайте



templates = Jinja2Templates(directory="templates")


# Разрешаем запросы с любых доменов
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





APP_DIR = os.path.abspath(os.path.dirname('__init__.py'))  # Определяем путь приложения
DB_DIR = os.path.join(APP_DIR, 'backend/db')  # Задаем путь для DB
if not os.path.exists(DB_DIR):  # Создаем если не существует
    os.makedirs(DB_DIR)

db = create_engine('sqlite:///' + os.path.join(DB_DIR, 'repo.db'), future=True)  # Создаем экземпляр db
