import sys
import os
import argparse
import asyncio
from app.core.data_transfer_objects.received_request import ReceivedRequest
from app.core.data_transfer_objects.answer import RequestResponse
import app.backend.database as db
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

rec_request = ReceivedRequest(url='CLI request', repo_path=args.repository_path, token=token)  # Формируем rec_request
resp_json = RequestResponse(data={}, error={}, meta={})  # Создаем экземпляр RequestResponse
instance_dbh = db.DataBaseHandler()  # Создаем экземпляр DataBaseHandler


async def main():
    global resp_json, instance_dbh, rec_request
    resp_json, code = await instance_dbh.get_report(rec_request=rec_request, resp_json=resp_json)
    print(f'{code} => {resp_json}')

# Запускаем асинхронную функцию
if __name__ == "__main__":
    asyncio.run(main())
