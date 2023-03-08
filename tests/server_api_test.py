import os
import argparse
import requests
from random import choice
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv

# Testing Setup
count_test = 500
web_server = False

logger.add('log_err.log', format='{time} {level} {message}', level='ERROR')
logger.add('log_warn.log', format='{time} {level} {message}', level='WARNING')
logger.add('log_info.log', format='{time:DD-MM HH:mm} {message}', level='INFO')

load_dotenv()
token = os.getenv('TOKEN')

with open('testing_list.txt', 'r') as file:
    testing_list = file.read().splitlines()

try:
    parser = argparse.ArgumentParser()
    parser.add_argument('test_count', nargs='?')
    args = parser.parse_args()
    if args.test_count:
        web_server = True
        test_count = int(args.test_count)
    else:
        test_count = count_test
except Exception as e:
    logger.warning(f'Count test ERROR! {e=} => test_count = 10')
    test_count = 10

if test_count > len(testing_list):
    logger.warning(f'Count test ERROR! {test_count=}, {len(testing_list)=}')
    test_count = len(testing_list)

if web_server:
    url = 'http://51.68.189.155'
else:
    url = 'http://127.0.0.1:8000'

for i in range(test_count):
    time = datetime.utcnow()
    query_type = choice(['GET', 'POST'])
    response_type = choice(['/api/repo', '/api/issues-statistic'])
    if response_type == '/api/repo':
        rt = 'repo'
    else:
        rt = 'full'
    random_repo = choice(testing_list)
    testing_list.remove(random_repo)
    skip_cache = choice([True, False])
    token_test = choice([token, None])
    i_test = f'[test={i+1}/{test_count}||{query_type}|{rt}|tok={bool(token_test)}|skip={skip_cache}]'

    if query_type == 'GET':
        url_test = url + response_type + '?name=' + random_repo
        if skip_cache == True:
            url_test += '&skipCache=True'
        headers = {'test': i_test, 'token': token_test}
        logger.info(f'>>>{i_test} {random_repo=}')
        try:
            response = requests.get(url_test, headers=headers)
        except requests.exceptions.ConnectTimeout as e:
            logger.error(f'<<<{i_test} ConnectTimeoutError! {random_repo=}, {e=}')
            continue

    else:
        url_test = url + response_type
        json = {
            'repositoryPath': random_repo,
            'skipCache': skip_cache,
            'token': token_test,
        }
        headers = {'test': i_test}
        logger.info(f'>>>{i_test} {random_repo=}')
        try:
            response = requests.post(url=url_test, json=json, headers=headers)
        except requests.exceptions.ConnectTimeout as e:
            logger.error(f'<<<{i_test} ConnectTimeoutError! {random_repo=}, {e=}')
            continue

    try:
        data = response.json()
    except:
        logger.error(f'<<<{i_test} ERROR! code={response.status_code}, {random_repo=}, {response.text=}')
        continue
    else:
        try:
            if data['meta']['code'] != 200:
                logger.error(f'<<<{i_test} ERROR! code={response.status_code}, {random_repo=}, {response.text=}')
                continue
            if not data['meta']['time']:
                logger.info(f'<<<{i_test} code={response.status_code}, time_deviation=DB_load, {random_repo=}, {response.text=}')
            else:
                time = datetime.utcnow() - time
                time = round(time.seconds + time.microseconds * 0.000001, 2)
                time_deviation = round(time - data['meta']['time'], 2)
                logger.info(f'<<<{i_test} code={response.status_code}, {time_deviation=}, {random_repo=}, {response.text=}')
        except Exception as e:
            logger.error(f'<<<{i_test} ERROR! code={response.status_code} {data=}, {e=}, {random_repo=}, {response.text=}')
