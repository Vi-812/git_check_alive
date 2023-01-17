import requests
import sys
import os
from dotenv import load_dotenv
load_dotenv()


class GraphqlAPI():
    def __init__(self, repository_owner, repository_name, cursor, labels_bug=None):
        self.url = 'https://api.github.com/graphql'
        self.headers = {'Authorization': 'token ' + os.getenv('TOKEN')}
        self.repository_owner = repository_owner
        self.repository_name = repository_name
        self.cursor = cursor
        self.labels_bug = labels_bug

    def get_info_labels_json(self):
        json = {
            'query':
            """
            query GetInfo ($owner: String!, $name: String!, $cursor: String) {
                repository(name: $name, owner: $owner) {
                    name
                    description
                    stargazerCount
                    createdAt
                    updatedAt
                    isArchived
                    labels(first: 100, after: $cursor) {
                        totalCount
                        pageInfo {
                            startCursor
                            endCursor
                            hasNextPage
                        }
                        edges {
                            cursor
                            node {
                                name
                            }
                        }
                    }
                    issues {
                        totalCount
                    }
                }
                rateLimit {
                    cost
                    remaining
                    resetAt
                }
            }
            """,
            'variables': {
                "owner": self.repository_owner,
                "name": self.repository_name,
                "cursor": self.cursor
            }
        }
        try:
            data = requests.post(url=self.url, headers=self.headers, json=json)
            data = data.json()
        except requests.exceptions.ConnectionError as err:
            print('--------------------------------------------------------------')
            print('Ошибка ссоединения с сервером')
            print(f'Исключение: {err}')
            sys.exit()
        return data

    def get_bug_issues_json(self):
        json = {
            'query':
            """
            query GetIssues($owner: String!, $name: String!, $labels: [String!], $cursor: String) {
                repository(name: $name, owner: $owner) {
                    issues(first: 100, filterBy: {labels: $labels}, after: $cursor) {
                        totalCount
                        pageInfo {
                            startCursor
                            endCursor
                            hasNextPage
                        }
                        edges {
                            cursor
                            node {
                                id
                                title
                                createdAt
                                closedAt
                                closed
                                updatedAt
                                comments(last: 1) {
                                    totalCount
                                    nodes {
                                        createdAt
                                    }
                                }
                            }
                        }
                    }
                }
                rateLimit {
                    cost
                    remaining
                    resetAt
                }
            }
            """,
            'variables': {
                "owner": self.repository_owner,
                "name": self.repository_name,
                "labels": self.labels_bug,
                "cursor": self.cursor
            }
        }
        try:
            data = requests.post(url=self.url, headers=self.headers, json=json)
            data = data.json()
        except requests.exceptions.ConnectionError as err:
            print('--------------------------------------------------------------')
            print('Ошибка ссоединения с сервером')
            print(f'Исключение: {err}')
            sys.exit()
        return data
