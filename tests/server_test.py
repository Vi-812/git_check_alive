import os
import requests
from random import choice
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv
load_dotenv()
logger.add('server_test.log', format='{time:DD-MM HH:mm} {message}', level='INFO',)

url = 'http://51.68.189.155/api'
token = os.getenv('TOKEN')

with open('test_repo.txt', 'r') as file:
    test_repositories = file.read().splitlines()

test_count = 1

for i in range(test_count):
    time = datetime.utcnow()
    random_repo = choice(test_repositories)
    logger.info(f'>>> i={i+1}/{test_count}, repo={random_repo}')
    test_repositories.remove(random_repo)
    json = {
        'token': token,
        'repository_path': random_repo
    }

    try:
        response = requests.post(url=url, json=json)
    except requests.exceptions.ConnectTimeout as e:
        logger.error(f'<<< ConnectTimeoutError! repo={random_repo}, e={e}')
        continue
    try:
        data = response.json()
    except:
        logger.error(f'<<< ERROR! code={response.status_code}, repo={random_repo}, response={response.text}')
        continue
    else:
        print(response.text)
        time = datetime.utcnow() - time
        time = round(time.seconds + time.microseconds * 0.000001, 2)
        time_deviation = round(time - data['meta']['time'], 2)
        logger.info(f'<<< code={response.status_code}, time_deviation={time_deviation}, repo={random_repo}, response={response.text}')
