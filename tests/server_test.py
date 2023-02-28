import os
import requests
from random import choice
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv
load_dotenv()

logger.add(
    'test_server.log',
    format='{time:DD-MM HH:mm} {message}',
    level='INFO',
    )

url = 'http://51.68.189.155/api'
token = os.getenv('TOKEN')

with open('test_repo.txt', 'r') as file:
    test_repositories = file.read().splitlines()

test_count = 10

for _ in range(test_count):
    time = datetime.utcnow()
    random_repo = choice(test_repositories)
    test_repositories.remove(random_repo)
    json = {
        'token': token,
        'repository_path': random_repo
    }

    response = requests.post(url=url, json=json)
    try:
        data = response.json()
    except:
        logger.error(f'ERROR! code="{response.status_code}", repo="{random_repo}", response="{response.text}"')
        continue
    else:
        time = datetime.utcnow() - time
        time = round(time.seconds + time.microseconds * 0.000001, 2)
        time_deviation = round(time - data['meta']['time'], 2)
        logger.info(f'OK! {time_deviation}, code="{response.status_code}", repo="{random_repo}", response="{response.text}"')
