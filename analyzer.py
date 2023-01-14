import requests
from tok import get_token


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

        # print(self.labels_count, '>>', self.labels_name)

        self.labels_bug = []
        for name in self.labels_name:
            if 'bug' in name.lower():
                self.labels_bug.append(name)

        print(self.labels_bug)

    def get_issues(self):
        self.cursor = None

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
                                'createdAt '
                                'closedAt '
                                'closed '
                                'lastEditedAt '
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
        print(self.json)

        data = requests.post(url=self.url, headers=self.headers, json=self.json)
        data = data.json()
        print(data)





x = GitGraphql()
x.get_info()
x.get_issues()