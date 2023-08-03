import os
import requests
from dotenv import load_dotenv
load_dotenv()

fast = False

url = 'http://127.0.0.1:8000/api/full'
token = os.getenv('TOKEN')

headers = {
    "Origin": "http://example.com",
}

if fast:  # При быстром тестировании, запускаем на проверку один репозиторий
    testing = [
        'https://github.com/vi-812/git_check_alive',
    ]
else:  # При полном тестировании, запускаем проверку ошибок и несколько репозиториев
    testing = [
        '--sub--zero--',
        'https://github.com/vi-812/git_',
        'https://github.com/vi-812/empty',
        'https://github.com/vi-812/git_check_alive',
        'https://github.com/pallets/flask',
        'https://github.com/facebook/jest',
    ]

if not fast:
    data = {  # Проверка ошибки неправильного токена
        'token': token[1:],
        'name': 'https://github.com/vi-812/git_'
    }
    response = requests.post(url=url, json=data, headers=headers)
    print(response.status_code, response.text)

for test in testing:  # Цикл тестов
    data = {
        'token': token,
        'name': test
    }
    response = requests.post(url=url, json=data, headers=headers)
    print(response.status_code, response.text)
    print(f'HEADERS>{response.headers}')
