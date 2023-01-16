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

xz = analyzer.GitGraphql(repository_owner, repository_name)
# xz = analyzer.GitGraphql('facebook', 'jest')
# xz = analyzer.GitGraphql('pallets', 'app')
xz.get_info_labels()
xz.get_bug_issues()
xz.analyz_bug_issues()

# Вывод данных пока не оформляю, ждем полный список
print('--------------------------------------------------------------')
print(f'Имя репозитория: {xz.repository_name}')
print(f'Владелец: {xz.repository_owner}')
print(f'Описание: {xz.description}')
print(f'Количество звезд: {xz.stars}')
print(f'Общее количество issue: {xz.issues_total_count}')
print(f'Issue bug-report: {xz.issues_bug_count}')
print(f'Из них открыты: {xz.issues_open_count}')
print(f'Из них закрыты: {xz.issues_closed_count}')
print(f'Время актуальности закрытых bug-report, минимальное: {xz.duration_closed_bug_min}')
print(f'максимальное: {xz.duration_closed_bug_max}')
print(f'медиана: {xz.duration_closed_bug_median}')
print(f'Время актуальности открытых bug-report, минимальное: {xz.duration_open_bug_min}')
print(f'максимальное: {xz.duration_open_bug_max}')
print(f'медиана: {xz.duration_open_bug_median}')
print(f'Остаток запросов: {xz.request_balance}({xz.request_cost})')
print('--------------------------------------------------------------')

