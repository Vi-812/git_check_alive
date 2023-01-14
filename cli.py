import argparse
import sys
import re
import analyzer

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
print('--------------------------------------------------------------')

xz = analyzer.GitGraphql(repository_owner, repository_name)
# xz = analyzer.GitGraphql('facebook', 'jest')
xz.get_info()
xz.get_issues()
xz.analyz()

print(f'Имя репозитория: {xz.repository_name}')
print(f'Владелец: {xz.repository_owner}')
print(f'Описание: {xz.description}')
print(f'Количество звезд: {xz.stars}')
print(f'Общее количество issue: {xz.issues_total_count}')
print(f'Issue bug-report: {xz.issues_bug_count}')
print(f'Из них открыты: {xz.issues_open_count}')
print(f'Из них закрыты: {xz.issues_closed_count}')
print(f'Время актуальности bug-report, минимальное: {xz.duration_fix_min}')
print(f'максимальное: {xz.duration_fix_max}')
print(f'среднее: {xz.duration_fix_avg}')
print(f'медиана: {xz.duration_fix_mediana}')
print(f'Остаток запросов: {xz.request_balance}({xz.request_cost})')
print('--------------------------------------------------------------')
