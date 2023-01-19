import requests
import sys

# Формировать json тут (кнопка Explorer)
# https://docs.github.com/ru/graphql/overview/explorer

class UseGraphQL():
    """
    ТОЖЕ ОПИСАТЕЛЬНОЕ
    """
    def __init__(self, repository_owner, repository_name, cursor, token, labels_bug=None):
        self.repository_owner = repository_owner
        self.repository_name = repository_name
        self.cursor = cursor
        self.token = token
        self.labels_bug = labels_bug

    def get_info_labels_json(self):
        json = {
            'query':
            """
            query GetInfo ($owner: String!, $name: String!, $cursor: String) {
                repository(name: $name, owner: $owner) {                    
                    name
                    owner {
                        login
                    }
                    description                    
                    homepageUrl
                    isInOrganization
                    licenseInfo {
                        name
                    }                    
                    stargazerCount
                    createdAt
                    updatedAt
                    pushedAt
                    isArchived
                    isDisabled
                    isLocked
                    isEmpty
                    isFork
                    issues {
                        totalCount
                    }
                    watchers {
                        totalCount
                    }
                    forkCount
                    pullRequests(last: 100) {
                        nodes {
                            publishedAt
                            lastEditedAt
                            closedAt
                            closed
                        }
                    }
                    labels(first: 100, after: $cursor) {
                        totalCount
                        pageInfo {
                            startCursor
                            endCursor
                            hasNextPage
                        }
                        edges {
                            node {
                                name
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
                "cursor": self.cursor
            }
        }
        instance_link = Link(self.token, json)
        data = instance_link.link()
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
                            node {
                                id
                                title
                                createdAt
                                updatedAt
                                closedAt
                                closed
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
        instance_link = Link(self.token, json)
        data = instance_link.link()
        return data


class Link():
    def __init__(self, token, json):
        self.url = 'https://api.github.com/graphql'
        self.headers = {'Authorization': 'token ' + token}
        self.json = json
    def link(self):
        try:
            data = requests.post(url=self.url, headers=self.headers, json=self.json)
            return data.json()
        except requests.exceptions.ConnectionError as err:
            print('--------------------------------------------------------------')
            print('Ошибка ссоединения с сервером')
            print(f'Исключение: {err}')
            sys.exit()
