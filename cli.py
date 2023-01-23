import sys
import os
import argparse
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



if testing:
    instance_api_client = github_api_client.GithubApiClient(token)
    instance_api_client.push_repository('vi-812/empty')
    return_json = instance_api_client.get_json()
    print(return_json)
    instance_api_client.push_repository('facebook/jest')
    return_json =instance_api_client.get_json()
else:
    instance_api_client = github_api_client.GithubApiClient(token)
    instance_api_client.push_repository(namespace.repository_path)
    return_json = instance_api_client.get_json()

print('--------------------------------------------------------------')
print(f'Имя репозитория: {instance_api_client.repository_name}')
print(f'Владелец: {instance_api_client.repository_owner}')
print(return_json)
print('--------------------------------------------------------------')
