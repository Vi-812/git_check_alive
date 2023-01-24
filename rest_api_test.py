import os
import requests
from dotenv import load_dotenv
load_dotenv()

url = 'http://localhost:8080/api'
token = os.getenv('TOKEN')

testing = [
    'vi-812/git_1',
    'vi-812/cli_git_api.py',
    'vi-812/git_check_alive',
    'vi-812/git_check_alive1',
    'https://github.com/pallets/flask',
]

for test in testing:
    body = {
        'token': token,
        'repository_path': test
    }
    response = requests.post(url=url, json=body)
    print(response.json())
