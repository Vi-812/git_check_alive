import os
from loguru import logger
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import uvicorn
from sqlalchemy import create_engine



PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(PROJECT_ROOT, 'backend/db')
os.makedirs(DB_DIR, exist_ok=True)

LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

logger.add(os.path.join(LOG_DIR, 'error.log'), format='{time} {level} {message}', level='ERROR')
logger.add(os.path.join(LOG_DIR, 'warning.log'), format='{time} {level} {message}', level='WARNING')
logger.add(os.path.join(LOG_DIR, 'info.log'), format='{time:DD-MM HH:mm} {message}', level='INFO')


db = create_engine('sqlite:///' + os.path.join(DB_DIR, 'repo.db'), future=True)  # Создаем экземпляр db


load_dotenv()
token_app = os.getenv('TOKEN')  # Загрузка токена, используется если пользователь не передал свой


app = FastAPI(
    timeout=1800,
    keep_alive=1800,
    secret_key = os.getenv('SECRET_KEY'),
)

# Подключение CORS с использованием переменной origins
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

# Подключение Jinja2
templates = Jinja2Templates(directory="templates")

from frontend.routes import router
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
