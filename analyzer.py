import requests
import sys
import os
import json
from datetime import datetime, timedelta
from statistics import median
from json_file import get_info_json
from dotenv import load_dotenv
load_dotenv()

# https://developer.chrome.com/docs/devtools/network/


class GitGraphql():
    """
    ОПИСАТЕЛЬНОЕ ОПИСАНИЕ
    """

    def __init__(self, repository_owner, repository_name):
        self.url = 'https://api.github.com/graphql'
        self.headers = {'Authorization': 'token ' + os.getenv('TOKEN')}
        self.repository_owner = repository_owner
        self.repository_name = repository_name


    def get_info_labels(self):
        self.cursor = None
        self.labels_name = []

        while True:

            self.json = get_info_json(self.repository_owner, self.repository_name, self.cursor)

            try:
                self.data = requests.post(url=self.url, headers=self.headers, json=self.json)
                self.data = self.data.json()
            except requests.exceptions.ConnectionError as err:
                print('--------------------------------------------------------------')
                print('Ошибка ссоединения с сервером')
                print(f'Исключение: {err}')
                sys.exit()

            self.parse_info_labesl()

            if self.has_next_page:
                self.cursor = self.end_cursor
            else:
                break

        self.labels_bug = []
        for name in self.labels_name:
            if 'bug' in name.lower():
                self.labels_bug.append(name)

    def parse_info_labesl(self):
        try:
            self.name = self.data['data']['repository']['name']
            self.description = self.data['data']['repository']['description']
            self.stars = self.data['data']['repository']['stargazerCount']
            self.created_at = self.data['data']['repository']['createdAt']
            self.updated_at = self.data['data']['repository']['updatedAt']
            self.archived = self.data['data']['repository']['isArchived']
            self.labels_count = self.data['data']['repository']['labels']['totalCount']
            self.start_cursor = self.data['data']['repository']['labels']['pageInfo']['startCursor']
            self.end_cursor = self.data['data']['repository']['labels']['pageInfo']['endCursor']
            self.has_next_page = self.data['data']['repository']['labels']['pageInfo']['hasNextPage']
            for label in self.data['data']['repository']['labels']['edges']:
                self.labels_name.append(label['node']['name'])
            self.issues_total_count = self.data['data']['repository']['issues']['totalCount']
            self.request_cost = self.data['data']['rateLimit']['cost']
            self.request_balance = self.data['data']['rateLimit']['remaining']
            self.request_reset = self.data['data']['rateLimit']['resetAt']
        except TypeError as err:
            print('--------------------------------------------------------------')
            print('При получении данных из репозитория возникла ошибка')
            print(f'Исключение: {err}')
            print(f"Тип ошибки: {self.data['errors'][0]['type']}")
            print(f"Сообщение: {self.data['errors'][0]['message']}")
            sys.exit()
        except KeyError as err:
            print('--------------------------------------------------------------')
            print('При получении данных из репозитория возникла ошибка')
            print('Ошибка при обращении по ключу')
            print(f'Ключ: {err}')
            sys.exit()


    def get_bug_issues(self):
        def to_date(date_str):
            return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
        self.cursor = None
        self.issues_dates_info = []
        self.duration_closed_bug_list = []
        self.duration_open_bug_list = []
        self.issues_open_count = 0
        self.issues_closed_count = 0

        while True:
            self.json = {
                'query': 'query GetIssues($owner: String!, $name: String!, $labels: [String!], $cursor: String) {'
                    'repository(name: $name, owner: $owner) {'
                        'issues(first: 100, filterBy: {labels: $labels}, after: $cursor) {'
                            'totalCount '
                            'pageInfo {'
                                'startCursor '
                                'endCursor '
                                'hasNextPage'
                            '}'
                            'edges {'
                                'cursor '
                                'node {'
                                    'id '
                                    'createdAt '
                                    'closedAt '
                                    'closed '
                                    'updatedAt '
                                    'comments(last: 1) {'
                                        'totalCount '
                                        'nodes {'
                                            'createdAt'
                                        '}'
                                    '}'
                                '}'
                            '}'
                        '}'
                    '}'
                    'rateLimit {'
                        'cost '
                        'remaining '
                        'resetAt'
                    '}'
                '}',
                'variables': {
                    "owner": self.repository_owner,
                    "name": self.repository_name,
                    "labels": self.labels_bug,
                    "cursor": self.cursor
                }
            }
            try:
                data = requests.post(url=self.url, headers=self.headers, json=self.json)
                data = data.json()
            except requests.exceptions.ConnectionError as err:
                print('--------------------------------------------------------------')
                print('Ошибка ссоединения с сервером')
                print(f'Исключение: {err}')
                sys.exit()

            try:
                self.issues_bug_count = data['data']['repository']['issues']['totalCount']
                self.start_cursor = data['data']['repository']['issues']['pageInfo']['startCursor']
                self.end_cursor = data['data']['repository']['issues']['pageInfo']['endCursor']
                self.has_next_page = data['data']['repository']['issues']['pageInfo']['hasNextPage']
                for issue in data['data']['repository']['issues']['edges']:
                    id_0 = issue['node']['id']
                    created_at_1 = to_date(issue['node']['createdAt'])
                    closed_at_2 = issue['node']['closedAt']
                    closed_bool = issue['node']['closed']
                    if bool(closed_at_2) and closed_bool:
                        self.issues_closed_count += 1
                        closed_at_2 = to_date(closed_at_2)
                        duration_fix_6 = closed_at_2 - created_at_1
                    elif not bool(closed_at_2) and not closed_bool:
                        self.issues_open_count += 1
                        duration_fix_6 = None
                    else:
                        duration_fix_6 = None
                        print(f'Ошибка! Несоответствие информации о закрытии issues с id = {id_0}, closed = '
                              f'{closed_bool}, closed_at = {closed_at_2}')
                    updated_at_3 = to_date(issue['node']['updatedAt'])
                    comments_count_4 = issue['node']['comments']['totalCount']
                    if issue['node']['comments']['nodes']:
                        comments_last_5 = to_date(issue['node']['comments']['nodes'][0]['createdAt'])
                    else:
                        comments_last_5 = None
                    self.issues_dates_info.append([
                        id_0,
                        created_at_1,
                        closed_at_2,
                        updated_at_3,
                        comments_count_4,
                        comments_last_5,
                        duration_fix_6
                    ])
                    if duration_fix_6:
                        self.duration_closed_bug_list.append(duration_fix_6)
                    else:
                        self.duration_open_bug_list.append(datetime.now() - created_at_1)
                    self.request_cost = data['data']['rateLimit']['cost']
                    self.request_balance = data['data']['rateLimit']['remaining']
                    self.request_reset = data['data']['rateLimit']['resetAt']
            except TypeError as err:
                print('--------------------------------------------------------------')
                print('При получении данных из репозитория возникла ошибка')
                print(f'Исключение: {err}')
                print(f"Тип ошибки: {data['errors'][0]['type']}")
                print(f"Сообщение: {data['errors'][0]['message']}")
                sys.exit()
            except KeyError as err:
                print('--------------------------------------------------------------')
                print('При получении данных из репозитория возникла ошибка')
                print('Ошибка при обращении по ключу')
                print(f'Ключ: {err}')
                sys.exit()
            if self.has_next_page:
                self.cursor = self.end_cursor
            else:
                break

    def analyz_bug_issues(self):
        if self.duration_closed_bug_list:
            self.duration_closed_bug_min = min(self.duration_closed_bug_list)
            self.duration_closed_bug_max = max(self.duration_closed_bug_list)
            self.duration_closed_bug_median = median(self.duration_closed_bug_list)
        else:
            self.duration_closed_bug_min = timedelta(days=0)
            self.duration_closed_bug_max = timedelta(days=0)
            self.duration_closed_bug_median = timedelta(days=0)

        if self.duration_open_bug_list:
            self.duration_open_bug_min = min(self.duration_open_bug_list)
            self.duration_open_bug_max = max(self.duration_open_bug_list)
            self.duration_open_bug_median = median(self.duration_open_bug_list)
        else:
            self.duration_open_bug_min = timedelta(days=0)
            self.duration_open_bug_max = timedelta(days=0)
            self.duration_open_bug_median = timedelta(days=0)
