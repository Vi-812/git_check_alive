import sys
import os
import argparse
import github_api_client as ga
from dotenv import load_dotenv
load_dotenv()

# Подробная информация о данных которые возможно получить из экземпляра класса в файле '\app\templates\help.html'

token = os.getenv('TOKEN')

try:
    parser = argparse.ArgumentParser()
    parser.add_argument('repository_path', nargs='?')
    namespace = parser.parse_args()
except:
    print('An error occurred, too many arguments were passed')
    print('Pass the link or "owner/repository_name" as an argument')
    print('"https://github.com/Vi-812/git_check_alive" or "vi-812/git_check_alive"')
    sys.exit()

if not namespace.repository_path:
    print('Pass the link or "owner/repository_name" as an argument')
    print('"https://github.com/Vi-812/git_check_alive" or "vi-812/git_check_alive"')
    sys.exit()

instance_api_client = ga.GithubApiClient(token)
return_json = instance_api_client.get_report(namespace.repository_path)

print(return_json)
