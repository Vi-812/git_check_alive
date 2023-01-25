import sys
import os
import argparse
import github_api_client as ga
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
    instance_api_client = ga.GithubApiClient(token)
    return_json = instance_api_client.get_report('vi-812/empty')
    print(return_json)
    return_json = instance_api_client.get_report('vi-812/cli_git_api.py')
    print(return_json)
    return_json = instance_api_client.get_report('facebook/jest')
else:
    instance_api_client = ga.GithubApiClient(token)
    return_json = instance_api_client.get_report(namespace.repository_path)

print('---')
print(f'Имя репозитория: {instance_api_client.repository_name}')
print(return_json)
print('---')
