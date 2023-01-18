import sys
import os
import argparse
import re
import github_api_client
from dotenv import load_dotenv
load_dotenv()

debug = True
testing = False

token = os.getenv('TOKEN')

try:
    parser = argparse.ArgumentParser()
    parser.add_argument('repository_path', nargs='?')
    namespace = parser.parse_args()
except:
    print('--------------------------------------------------------------')
    print('Возникла ошибка, передано слишком много аргументов')
    print('Передайте аргументом ссылку или владельца/имя репозитория')
    print('"https://github.com/Vi-812/git" либо "Vi-812/git"')
    sys.exit()

# DEBUG TRUE
if not namespace.repository_path:
    if debug is False:
        print('Передайте аргументом ссылку или владельца/имя репозитория')
        print('"https://github.com/Vi-812/git" либо "Vi-812/git"')
        sys.exit()
    else:
        namespace.repository_path = 'https://github.com/Vi-812/git_check_alive'

data = re.search('([^/]+/[^/]+)$', namespace.repository_path)
if data:
    data = data.group(1)
    repository_owner, repository_name = data.split('/', 2)
else:
    print('Ссылка не корректна, введите ссылку в формате')
    print('"https://github.com/Vi-812/git" либо "Vi-812/git"')
    sys.exit()

if testing:
    instance_api_client = github_api_client.GithubApiClient(token)
    instance_api_client.push_repository('vi-812', 'empty')
    return_json = instance_api_client.get_json()
    print(return_json)

    instance_api_client = github_api_client.GithubApiClient(token)
    instance_api_client.push_repository('facebook', 'jest')
    return_json = instance_api_client.get_json()
    print(return_json)
else:
    instance_api_client = github_api_client.GithubApiClient(token)
    instance_api_client.push_repository(repository_owner, repository_name)
    return_json = instance_api_client.get_json()
    print(return_json)

print('--------------------------------------------------------------')
print(f'Имя репозитория: {instance_api_client.repository_name}')
print(f'Владелец: {instance_api_client.repository_owner}')
print(f'Создан: {instance_api_client.repo_created_at}')
print(f'Обновлен: {instance_api_client.repo_updated_at}')
print(f'Общее количество issue: {instance_api_client.repo_issues_total_count}')
print(f'Issue bug-report: {instance_api_client.issues_bug_count}')
print(f'Из них открыты: {instance_api_client.issues_open_count}')
print(f'Из них закрыты: {instance_api_client.issues_closed_count}')
print('--------------------------------------------------------------')
