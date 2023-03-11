import requests
import re


def scraping_testing_list():
    url = 'https://habr.com/ru/post/453444/'
    html_text = requests.get(url).text

    regex = re.compile(r'Репозиторий: <a href="(https://github.com/.+/.+)">')
    scrap_repo = regex.findall(html_text)

    with open('testing_list.txt', 'w') as file:
        for repo in scrap_repo:
            file.write(repo + '\n')


scraping_testing_list()
