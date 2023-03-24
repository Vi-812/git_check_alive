import os
import requests
from dotenv import load_dotenv
load_dotenv()

fast = False

url = 'http://127.0.0.1:8000/api/full'
token = os.getenv('TOKEN')

if fast:
    testing = [
        'https://github.com/vi-812/git_check_alive',
    ]
else:
    testing = [
        '--sub--zero--',
        'https://github.com/vi-812/git_',
        'https://github.com/vi-812/empty',
        'https://github.com/vi-812/git_check_alive',
        'https://github.com/pallets/flask',
        'https://github.com/facebook/jest',
    ]

if not fast:
    data = {
        'token': token[1:],
        'name': 'https://github.com/vi-812/git_'
    }
    response = requests.post(url=url, json=data)
    print(response.status_code, response.text)

for test in testing:
    data = {
        'token': token,
        'name': test
    }
    response = requests.post(url=url, json=data)
    print(response.status_code, response.text)
