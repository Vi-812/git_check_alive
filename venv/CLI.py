from github import Github
import sys
import re


while True:
    adr = input('Вставьте ссылку на репозиторий (q - выход): ')

    if adr == 'q' or adr == 'Q':
        sys.exit()

    if adr == ' ':
        adr = 'https://github.com/Vi-812/GIT'

    adress = re.search('github.com/(.+/.+)', adr)
    if adress:
        adress = adress.group(1)
    else:
        adress = re.search('//?(.+/.+)', adr)
        if adress:
            adress = adress.group(1)

    if adress:
        break
    else:
        print('Ссылка не корректна, введите ссылку в формате')
        print('"https://github.com/Vi-812/GIT" либо "Vi-812/GIT"')
        print('Либо введите Q для выхода')

g = Github()
repo = g.get_repo(adress)
print(f'Наименование: {repo.name}')
print(f'Описание: {repo.description}')
print(f'Рейтинг: {repo.stargazers_count}')
