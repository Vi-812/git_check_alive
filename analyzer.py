import requests
import datetime
from tok import get_token # Убрать))


class GitGraphql:
    """
    ОПИСАТЕЛЬНОЕ ОПИСАНИЕ
    """

    def __init__(self):
        self.url = 'https://api.github.com/graphql'
        self.headers = {'Authorization': 'token ' + get_token()}
        # Импортировать данные
        self.repository_owner = 'facebook'
        self.repository_name = 'jest'

    def get_info(self):
        self.cursor = None
        self.labels_name = []

        while True:
            self.json = { # Всего иссуес ??
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
            # print(self.json)

            data = requests.post(url=self.url, headers=self.headers, json=self.json)
            data = data.json()
            # print(data)

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
            self.request_cost = data['data']['rateLimit']['cost']
            self.request_balance = data['data']['rateLimit']['remaining']
            self.request_reset = data['data']['rateLimit']['resetAt']
            if self.has_next_page:
                self.cursor = self.end_cursor
            else:
                break

        # print(self.labels_count, '=', len(self.labels_name), '>>', self.labels_name)

        self.labels_bug = []
        for name in self.labels_name:
            if 'bug' in name.lower():
                self.labels_bug.append(name)

        # print(self.labels_bug)

    def get_issues(self):
        def to_date(date_str):
            date_dt = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
            return date_dt

        self.cursor = None
        self.issues_dates_info = []
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
            # print(self.json)

            data = requests.post(url=self.url, headers=self.headers, json=self.json)
            data = data.json()
            # print(data)

            self.issues_count = data['data']['repository']['issues']['totalCount']
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
                    print(f'Ошибка! Несоответствие информации о закрытии issues с id = {id_0}, closed = {closed_bool}, closed_at = {closed_at_2}')
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
            if self.has_next_page:
                self.cursor = self.end_cursor
            else:
                break

        print(self.issues_count, self.issues_open_count, self.issues_closed_count)
        print(len(self.issues_dates_info))

        print(self.request_cost, self.request_balance)











x = GitGraphql()
x.get_info()
x.get_issues()