import os
import sys
import requests
import random
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv
load_dotenv()

logger.add('get_test.log', format='{time:DD-MM HH:mm} {message}', level='INFO')

token = os.getenv('TOKEN')

try:
    # response = requests.get('https://isgitalive.karo-dev.ru/api/repo?name=vi-812/git_check_alive')
    # response = requests.get('http://127.0.0.1:8000/api/issues-statistic?name=vi-812/git_check_alive')
    # response = requests.get('http://127.0.0.1:8000/api/issues-statistic?name=facebook/jest&cache=False')
    response = requests.get('http://127.0.0.1:8000/api/repo?name=facebook/jest&cache=True')
    data = response.json()
except Exception as e:
    logger.error(f'code="", repo="", response="", e="{e}"')
    sys.exit()
else:
    print(response.status_code, data)
