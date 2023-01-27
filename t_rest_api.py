import os
import requests
from dotenv import load_dotenv
load_dotenv()

mega_test = True

url = 'http://localhost:8080/api'
token = os.getenv('TOKEN')

if not mega_test:
    testing = [
        'vi-812/empty',
        'vi-812/git_check_alive',
        'https://github.com/pallets/flask',
    ]
else:
    testing = [
        'zero',
        'vi-812/git_',
        'vi-812/empty',
        'vi-812/git_check_alive',
        'https://github.com/pallets/flask',
        'facebook/jest',
        'https://github.com/dbeaver/dbeaver',
    ]

for test in testing:
    body = {
        'token': token,
        'repository_path': test
    }
    response = requests.post(url=url, json=body)
    print(response.status_code, response.text)
