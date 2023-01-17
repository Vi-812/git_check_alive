import sys
import os
import argparse
import re
import analyzer
from dotenv import load_dotenv
load_dotenv()

debug = True
testing = True

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
    github_api = analyzer.GraphqlClient('facebook', 'jest', os.getenv('TOKEN'))
    github_api.get_info_labels()
    github_api.get_bug_issues()
    github_api.analyz_bug_issues()
    github_api.get_json()
    print('--------------------------------------------------------------')
    print(f'Имя репозитория: {github_api.repository_name}')
    print(f'Владелец: {github_api.repository_owner}')
    print(f'Создан: {github_api.repo_created_at}')
    print(f'Обновлен: {github_api.repo_updated_at}')
    print(f'Общее количество issue: {github_api.repo_issues_total_count}')
    print(f'Issue bug-report: {github_api.issues_bug_count}')
    print(f'Из них открыты: {github_api.issues_open_count}')
    print(f'Из них закрыты: {github_api.issues_closed_count}')
    print(f'Время актуальности закрытых bug-report, минимальное: {github_api.duration_closed_bug_min}')
    print(f'максимальное: {github_api.duration_closed_bug_max}')
    print(f'медиана: {github_api.duration_closed_bug_median}')
    print(f'Время актуальности открытых bug-report, минимальное: {github_api.duration_open_bug_min}')
    print(f'максимальное: {github_api.duration_open_bug_max}')
    print(f'медиана: {github_api.duration_open_bug_median}')
    print(f'Стоимость: {github_api.request_total_cost}, время: {github_api.request_duration_time}, баланс: {github_api.request_balance}')
    print('--------------------------------------------------------------')
    github_api = analyzer.GraphqlClient('vi-812', 'empty', os.getenv('TOKEN'))
    github_api.get_info_labels()
    github_api.get_bug_issues()
    github_api.analyz_bug_issues()
    github_api.get_json()
    print('--------------------------------------------------------------')
    print(f'Имя репозитория: {github_api.repository_name}')
    print(f'Владелец: {github_api.repository_owner}')
    print(f'Создан: {github_api.repo_created_at}')
    print(f'Обновлен: {github_api.repo_updated_at}')
    print(f'Общее количество issue: {github_api.repo_issues_total_count}')
    print(f'Issue bug-report: {github_api.issues_bug_count}')
    print(f'Из них открыты: {github_api.issues_open_count}')
    print(f'Из них закрыты: {github_api.issues_closed_count}')
    print(f'Время актуальности закрытых bug-report, минимальное: {github_api.duration_closed_bug_min}')
    print(f'максимальное: {github_api.duration_closed_bug_max}')
    print(f'медиана: {github_api.duration_closed_bug_median}')
    print(f'Время актуальности открытых bug-report, минимальное: {github_api.duration_open_bug_min}')
    print(f'максимальное: {github_api.duration_open_bug_max}')
    print(f'медиана: {github_api.duration_open_bug_median}')
    print(f'Стоимость: {github_api.request_total_cost}, время: {github_api.request_duration_time}, баланс: {github_api.request_balance}')
    print('--------------------------------------------------------------')
else:
    github_api = analyzer.GraphqlClient(repository_owner, repository_name, os.getenv('TOKEN'))
    github_api.get_info_labels()
    github_api.get_bug_issues()
    github_api.analyz_bug_issues()
    github_api.get_json()
    print('--------------------------------------------------------------')
    print(f'Имя репозитория: {github_api.repository_name}')
    print(f'Владелец: {github_api.repository_owner}')
    print(f'Создан: {github_api.repo_created_at}')
    print(f'Обновлен: {github_api.repo_updated_at}')
    print(f'Общее количество issue: {github_api.repo_issues_total_count}')
    print(f'Issue bug-report: {github_api.issues_bug_count}')
    print(f'Из них открыты: {github_api.issues_open_count}')
    print(f'Из них закрыты: {github_api.issues_closed_count}')
    print(f'Время актуальности закрытых bug-report, минимальное: {github_api.duration_closed_bug_min}')
    print(f'максимальное: {github_api.duration_closed_bug_max}')
    print(f'медиана: {github_api.duration_closed_bug_median}')
    print(f'Время актуальности открытых bug-report, минимальное: {github_api.duration_open_bug_min}')
    print(f'максимальное: {github_api.duration_open_bug_max}')
    print(f'медиана: {github_api.duration_open_bug_median}')
    print(f'Стоимость: {github_api.request_total_cost}, время: {github_api.request_duration_time}, баланс: {github_api.request_balance}')
    print('--------------------------------------------------------------')
