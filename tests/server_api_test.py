import os
import argparse
import requests
from random import choice
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv

# Testing Setup
count_test = 100
web_server = False

logger.add('log_err.log', format='{time} {level} {message}', level='ERROR')
logger.add('log_warn.log', format='{time} {level} {message}', level='WARNING')
logger.add('log_info.log', format='{time:DD-MM HH:mm} {message}', level='INFO')

load_dotenv()
token = os.getenv('TOKEN')

with open('testing_list.txt', 'r') as file:  # Считываем testing_list из файла
    testing_list = file.read().splitlines()

try:  # Парсим аргументы командной строки
    parser = argparse.ArgumentParser()
    parser.add_argument('test_count', nargs='?')
    args = parser.parse_args()
    if args.test_count:  # Если количество тестов было передано через аргументы командной строки
        web_server = True  # Тестируем Web-Server (игнорируя Testing Setup)
        test_count = int(args.test_count)
    else:
        test_count = count_test
except Exception as e:
    logger.warning(f'Count test ERROR! {e=} => test_count = 10')
    test_count = 10

if test_count > len(testing_list):  # Контроль количества тестов, не должен превышать testing_list
    logger.warning(f'Count test ERROR! {test_count=}, {len(testing_list)=}')
    test_count = len(testing_list)

if web_server:  # Выбор между Web и Local серверами
    url = 'http://51.68.189.155'
else:
    url = 'http://127.0.0.1:8000'

for i in range(test_count):  # Цикл тестов
    time = datetime.utcnow()  # Засекаем время
    query_type = choice(['GET', 'POST'])  # Определяем тип запроса
    response_type = choice(['/api/repo', '/api/issues-statistic', '/api/full'])  # Определяем тип ответа
    if response_type == '/api/repo':  # Сокращенный тип ответа (для i_test)
        rt = 'repo'
    elif response_type == '/api/issues-statistic':
        rt = 'issues'
    else:
        rt = 'full'
    random_repo = choice(testing_list)  # Определяем репозиторий для тестирования
    testing_list.remove(random_repo)  # Удаляем выбранный репозиторий из testing_list
    skip_cache = choice([True, False])  # Определяем skip_cache, разрешена ли загрузка из базы данных
    token_test = choice([token, None])  # Определяем передавать ли токен
    # Формируем переменную i_test, как идентификатор текущего теста
    i_test = f'[test={i+1}/{test_count}||{query_type}|{rt}|tok={bool(token_test)}|skip={skip_cache}]'

    if query_type == 'GET':  # Составляем GET запрос
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

    else:  # Составляем POST запрос
        url_test = url + response_type
        json = {
            'name': random_repo,
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
