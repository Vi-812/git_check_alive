import os
import requests
from dotenv import load_dotenv
load_dotenv()

url = 'http://localhost:8080/api'
token = os.getenv('TOKEN')

testing = [
    'vi-812/git_',
    'vi-812/empty',
    'vi-812/git_check_alive',
    'https://github.com/pallets/flask',
]

for test in testing:
    body = {
        'token': token,
        'repository_path': test
    }
    response = requests.post(url=url, json=body)
    print(response.json())
