import sys
import os
import argparse
import github_api_client
from dotenv import load_dotenv
load_dotenv()

debug = True
testing = True

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



if testing:
    instance_api_client = github_api_client.GithubApiClient(token)
    instance_api_client.get_report('vi-812/empty')
    return_json = instance_api_client.get_json()
    print(return_json)
    instance_api_client.get_report('vi-812/cli_git_api.py')
    return_json = instance_api_client.get_json()
    print(return_json)
    instance_api_client.get_report('facebook/jest')
    return_json =instance_api_client.get_json()
else:
    instance_api_client = github_api_client.GithubApiClient(token)
    instance_api_client.get_report(namespace.repository_path)
    return_json = instance_api_client.get_json()

print('--------------------------------------------------------------')
print(f'Имя репозитория: {instance_api_client.repository_name}')
print(f'Медиана closed: {instance_api_client.duration_closed_bug_50percent}, '
      f'open: {instance_api_client.duration_open_bug_50percent}')
print(f'Обновлен: {instance_api_client.repo_updated_at}, pushed: {instance_api_client.repo_pushed_at}')
print(return_json)
print('--------------------------------------------------------------')
