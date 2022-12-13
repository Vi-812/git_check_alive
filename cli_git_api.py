from github import Github, GithubException, UnknownObjectException
import sys
import argparse
import re


def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('repository', nargs='?')
    return parser

if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args()

    if not namespace.repository:
        print('Укажите ссылку либо имя репозитория')
        sys.exit()
    if namespace.repository == '1':
        namespace.repository = 'https://github.com/Vi-812/git_check_alive'
    # print(namespace.repository)

    adress = re.search('([^/]+/[^/]+)$', namespace.repository)
    if adress:
        adress = adress.group(1)
    # print(adress)
    if not adress:
        print('Ссылка не корректна, введите ссылку в формате')
        print('"https://github.com/Vi-812/GIT" либо "Vi-812/GIT"')
        sys.exit()
    # print(adress)

    try:
        g = Github()
        repo = g.get_repo(adress)
        print(f'Наименование: {repo.name}')
        print(f'Описание: {repo.description}')
        print(f'Рейтинг: {repo.stargazers_count}')

    except UnknownObjectException:
        print('Указанного вами репозитория не существует')

    except:
        print('Ошибка, возможно нет интернета =)')
