import requests
import argparse
import sys
import re
from tok import get_token


debug = True


# Надо обработать ошибку передачи нескольких аргументов
parser = argparse.ArgumentParser()
parser.add_argument('repository_path', nargs='?')
namespace = parser.parse_args()

if not namespace.repository_path:
    if debug == False:
        print('Передайте аргументом ссылку или владельца/имя репозитория')
        print('"https://github.com/Vi-812/GIT" либо "Vi-812/git"')
        sys.exit()
    else:
        namespace.repository_path = 'https://github.com/Vi-812/git_check_alive'
if namespace.repository_path == '1':
    namespace.repository_path = 'https://github.com/Vi-812/git_check_alive'

data = re.search('([^/]+/[^/]+)$', namespace.repository_path)
if data:
    data = data.group(1)
    repository_owner, repository_name = data.split('/', 2)
else:
    print('Ссылка не корректна, введите ссылку в формате')
    print('"https://github.com/Vi-812/GIT" либо "Vi-812/git"')
    sys.exit()

print(f'Имя владельца: {repository_owner}')
print(f'Имя репозитория: {repository_name}')


url = 'https://api.github.com/graphql'
api_token = 'token ' + get_token()
headers = {'Authorization': api_token}

# Это просто дичь какая то))
json = {
    'query': '{'
        f'repository(owner: "{repository_owner}", name: "{repository_name}") ' + '{'
            'name\n'
            'description\n'
            'stargazerCount\n'
            'labels (first: 100) {'
                'totalCount\n'
                'nodes {'
                    'name'
                '}'
            '}'
            'issues(first: 100) {'
                'totalCount\n'
                'nodes {'
                    'title\n'
                    'closed\n'
                    'labels (first: 100) {'
                        'totalCount\n'
                        'nodes {'
                            'name'
                        '}'
                    '}'
                '}'
            '}'
        '}'
        'rateLimit {'
            'cost\n'
            'remaining'
        '}'
    '}'
}

# Необходимо будет улучшить обработку исключений
try:
    data = requests.post(headers=headers, json=json, url=url)
    data = data.json()
except:
    print('Чота не так)')
    sys.exit()

name_js = data['data']['repository']['name']
description_js = data['data']['repository']['description']
stars_count_js = data['data']['repository']['stargazerCount']

labels_total_js = data['data']['repository']['labels']['totalCount']
labels_list_js = []
labels_bug_js = 0
for label in data['data']['repository']['labels']['nodes']:
    labels_list_js.append(label['name'])
    if 'bug' in label['name']:
        labels_bug_js += 1

# Сделать обработку на 100+ багрепортов и 100+ меток в репозитории!!!
issues_total_js = data['data']['repository']['issues']['totalCount']
issues_get_js = issues_open_bug_js = issues_closed_bug_js = issues_open_nobug_js = issues_closed_nobug_js = 0
for issue in data['data']['repository']['issues']['nodes']:
    issues_get_js += 1
    issue_bug = 0
    for issue_label in issue['labels']['nodes']:
        if 'bug' in issue_label['name']:
            issue_bug += 1
    if issue_bug > 0:
        if issue['closed'] == False:
            issues_open_bug_js += 1
        else:
            issues_closed_bug_js += 1
    else:
        if issue['closed'] == False:
            issues_open_nobug_js += 1
        else:
            issues_closed_nobug_js +=1

limit_cost_js = data['data']['rateLimit']['cost']
limit_remaining_js = data['data']['rateLimit']['remaining']

print('--------------------------------------------------------------')
print(f'Наименование: {name_js}')
print(f'Описание: {description_js}')
print(f'Количество звезд: {stars_count_js}')
print(f'Проверено issues: {issues_get_js}, всего issues в репозитории: {issues_total_js}')
print(f'Issues с меткой "bug": открытых - {issues_open_bug_js}, закрытых - {issues_closed_bug_js}, всего - '
      f'{issues_open_bug_js + issues_closed_bug_js}')
print(f'Всего меток: {labels_total_js}, из них с меткой "bug": {labels_bug_js}')
print(f'Список меток: {labels_list_js}')
print('--------------------------------------------------------------')
print(f'Стоимость запроса: {limit_cost_js}, остаток запросов: {limit_remaining_js}')