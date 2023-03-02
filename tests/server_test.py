import os
import argparse
import requests
from random import choice
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv
logger.add('server_test.log', format='{time:DD-MM HH:mm} {message}', level='INFO',)
load_dotenv()
token = os.getenv('TOKEN')
url = 'http://51.68.189.155/api'

with open('test_repo.txt', 'r') as file:
    test_repositories = file.read().splitlines()

try:
    parser = argparse.ArgumentParser()
    parser.add_argument('test_count', nargs='?')
    args = parser.parse_args()
    if args.test_count:
        test_count = int(args.test_count)
    else:
        test_count = 10
except Exception as e:
    logger.error(f'Count test ERROR! e={e} => test_count = 10')
    test_count = 10

if test_count > len(test_repositories):
    logger.error(f'Count test ERROR! test_count={test_count}, repositories={len(test_repositories)}')
    test_count = len(test_repositories)

for i in range(test_count):
    time = datetime.utcnow()
    random_repo = choice(test_repositories)
    logger.info(f'>>> (i={i+1}/{test_count}) repo={random_repo}')
    test_repositories.remove(random_repo)
    json = {
        'token': token,
        'repository_path': random_repo
    }

    try:
        response = requests.post(url=url, json=json)
    except requests.exceptions.ConnectTimeout as e:
        logger.error(f'<<< (i={i+1}/{test_count}) ConnectTimeoutError! repo={random_repo}, e={e}')
        continue
    try:
        data = response.json()
    except:
        logger.error(f'<<< (i={i+1}/{test_count}) ERROR! code={response.status_code}, repo={random_repo}, response={response.text}')
        continue
    else:
        print(response.text)
        time = datetime.utcnow() - time
        time = round(time.seconds + time.microseconds * 0.000001, 2)
        time_deviation = round(time - data['meta']['time'], 2)
        logger.info(f'<<< (i={i+1}/{test_count}) code={response.status_code}, time_deviation={time_deviation}, repo={random_repo}, response={response.text}')
