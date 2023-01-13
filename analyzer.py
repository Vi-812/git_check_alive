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
        self.json = {
            'query GetInfo($owner: String!, $name: String!)': '{'
                'repository(name: $name, owner: $owner) {'
                    'name\n'
                    'description\n'
                    'stargazerCount\n'
                    'createdAt\n'
                    'updatedAt\n'
                    'isArchived\n'
                    'labels(first: 2, after: "NA") {' # Встроить переменные
                        'totalCount\n'
                        'pageInfo {'
                            'startCursor\n'
                            'endCursor\n'
                            'hasNextPage'
                        '}'
                        'edges {'
                            'cursor\n'
                            'node {'
                                'name'
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
        params = {
            'owner': '"facebook"',
            'name': '"jest"'
        }

        data = requests.post(url=self.url, headers=self.headers, json=self.json, params=params)
        data = data.json()
        print(data)

x = GitGraphql()
x.get_info()