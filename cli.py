import sys
import os
import argparse
import asyncio
from dto.received_request import ReceivedRequest
import backend.database as db
from dotenv import load_dotenv
load_dotenv()

token = os.getenv('TOKEN')

try:  # Парсим аргументы командной строки
    parser = argparse.ArgumentParser()
    parser.add_argument('repository_path', nargs='?')
    args = parser.parse_args()
except:  # Обработка ошибки, слишком много аргументов
    print('An error occurred, too many arguments were passed')
    print('Pass the link or "owner/repository_name" as an argument')
    print('"https://github.com/Vi-812/git_check_alive" or "vi-812/git_check_alive"')
    sys.exit()

if not args.repository_path:  # Обработка ошибки, не передано аргумента
    print('Pass the link or "owner/repository_name" as an argument')
    print('"https://github.com/Vi-812/git_check_alive" or "vi-812/git_check_alive"')
    sys.exit()

rec_request = ReceivedRequest(url='CLI request', repo_path=args.repository_path, token=token)  # формируем rec_request
instance_dbh = db.DataBaseHandler()  # Создаем экземпляр DataBaseHandler
resp_json, code = asyncio.run(instance_dbh.get_report(rec_request=rec_request))  # Делаем запрос

print(f'{code} => {resp_json}')
