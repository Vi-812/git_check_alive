import os
import sys
from loguru import logger
from sqlalchemy import create_engine
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


current_file = os.path.abspath(sys.argv[0])
PROJECT_ROOT = os.path.dirname(os.path.abspath(current_file))

LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

logger.add(os.path.join(LOG_DIR, 'error.log'), format='{time} {level} {message}', level='ERROR')
logger.add(os.path.join(LOG_DIR, 'warning.log'), format='{time} {level} {message}', level='WARNING')
logger.add(os.path.join(LOG_DIR, 'info.log'), format='{time:DD-MM HH:mm} {message}', level='INFO')

DB_DIR = os.path.join(PROJECT_ROOT, 'db')
os.makedirs(DB_DIR, exist_ok=True)
db = create_engine('sqlite:///' + os.path.join(DB_DIR, 'repo.db'), future=True)  # Создаем экземпляр db

load_dotenv()
token_app = os.getenv('TOKEN')  # Загрузка токена, используется если пользователь не передал свой

templates = Jinja2Templates(directory=os.path.join(PROJECT_ROOT, "frontend", "templates"))

app = FastAPI(
    timeout=1800,
    keep_alive=1800,
    secret_key=os.getenv('SECRET_KEY'),
)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
