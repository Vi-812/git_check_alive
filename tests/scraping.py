import requests
import re

url = 'https://habr.com/ru/post/453444/'
html_text = requests.get(url).text

regex = re.compile(r'Репозиторий: <a href="(https://github.com/.+/.+)">')
scrap_repo = regex.findall(html_text)

with open('test_repo.txt', 'w') as file:
    for repo in scrap_repo:
        file.write(repo + '\n')
