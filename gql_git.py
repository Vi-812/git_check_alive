import argparse
import sys
import re
from analyzer import GitGraphql


debug = True


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

print(f'Имя владельца: {repository_owner}')
print(f'Имя репозитория: {repository_name}')

x = GitGraphql(repository_owner, repository_name)
x.get_info()
x.get_issues()



# try:
#
# except requests.exceptions.ConnectionError as err:
#     print('--------------------------------------------------------------')
#     print('Ошибка ссоединения с сервером')
#     print(f'Исключение: {err}')
#     sys.exit()

# try:
#
# except TypeError as err:
#     print('--------------------------------------------------------------')
#     print('При получении данных из репозитория возникла ошибка')
#     print(f'Исключение: {err}')
#     print(f"Тип ошибки: {data['errors'][0]['type']}")
#     print(f"Сообщение: {data['errors'][0]['message']}")
#     sys.exit()


