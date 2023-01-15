import requests
import datetime
import sys
import os
from statistics import median
from dotenv import load_dotenv
load_dotenv()
# https://www.w3schools.com/python/python_json.asp
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

    def get_info(self):
        self.cursor = None
        self.labels_name = []

        while True:
            self.json = {
                'query': 'query GetInfo ($owner: String!, $name: String!, $cursor: String) {'
                    'repository(name: $name, owner: $owner) {'
                        'name '
                        'description '
                        'stargazerCount '
                        'createdAt '
                        'updatedAt '
                        'isArchived '
                        'labels(first: 100, after: $cursor) {'
                            'totalCount '
                            'pageInfo {'
                                'startCursor '
                                'endCursor '
                                'hasNextPage'
                            '}'
                            'edges {'
                                'cursor '
                                'node {'
                                    'name'
                                '}'
                            '}'
                        '}'
                        'issues {'
                            'totalCount'
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
                self.name = data['data']['repository']['name']
                self.description = data['data']['repository']['description']
                self.stars = data['data']['repository']['stargazerCount']
                self.created_at = data['data']['repository']['createdAt']
                self.updated_at = data['data']['repository']['updatedAt']
                self.archived = data['data']['repository']['isArchived']
                self.labels_count = data['data']['repository']['labels']['totalCount']
                self.start_cursor = data['data']['repository']['labels']['pageInfo']['startCursor']
                self.end_cursor = data['data']['repository']['labels']['pageInfo']['endCursor']
                self.has_next_page = data['data']['repository']['labels']['pageInfo']['hasNextPage']
                for label in data['data']['repository']['labels']['edges']:
                    self.labels_name.append(label['node']['name'])
                self.issues_total_count = data['data']['repository']['issues']['totalCount']
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
            if self.has_next_page:
                self.cursor = self.end_cursor
            else:
                break

        self.labels_bug = []
        for name in self.labels_name:
            if 'bug' in name.lower():
                self.labels_bug.append(name)

    def get_issues(self):
        def to_date(date_str):
            return datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
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
                        self.duration_open_bug_list.append(datetime.datetime.now() - created_at_1)
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
            if self.has_next_page:
                self.cursor = self.end_cursor
            else:
                break

    def data_analyz(self):
        if self.duration_closed_bug_list:
            self.duration_closed_bug_min = min(self.duration_closed_bug_list)
            self.duration_closed_bug_max = max(self.duration_closed_bug_list)
            self.duration_closed_bug_median = median(self.duration_closed_bug_list)
        else:
            self.duration_closed_bug_min = datetime.timedelta(days=0)
            self.duration_closed_bug_max = datetime.timedelta(days=0)
            self.duration_closed_bug_median = datetime.timedelta(days=0)

        if self.duration_open_bug_list:
            self.duration_open_bug_min = min(self.duration_open_bug_list)
            self.duration_open_bug_max = max(self.duration_open_bug_list)
            self.duration_open_bug_median = median(self.duration_open_bug_list)
        else:
            self.duration_open_bug_min = datetime.timedelta(days=0)
            self.duration_open_bug_max = datetime.timedelta(days=0)
            self.duration_open_bug_median = datetime.timedelta(days=0)

