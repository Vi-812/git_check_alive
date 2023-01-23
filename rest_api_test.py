import os
import requests
from dotenv import load_dotenv
load_dotenv()

url = 'http://localhost:8080/api'
token = os.getenv('TOKEN')
body = {
    'token': token,
    'repository_path': 'vi-812/git_check_alive'
}
response = requests.post(url=url, json=body)
print(response.json())