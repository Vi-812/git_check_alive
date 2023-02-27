import os
import sys
import requests
import random
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv
load_dotenv()

logger.add(
    'no_local_test.log',
    format='{time:DD-MM HH:mm} {message}',
    level='INFO',
    )

token = os.getenv('TOKEN')

try:
    response = requests.get('http://127.0.0.1:8000/api/repo?name=vi-812/git_check_alive')
    data = response.json()
except Exception as e:
    logger.error(f'code="", repo="", response="", e="{e}"')
    sys.exit()
else:
    print(response.status_code, data)
