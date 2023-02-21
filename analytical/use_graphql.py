import aiohttp
import requests
from loguru import logger
import json
from req_response import resp_json


# Сформировать json можно тут (кнопка Explorer)
# https://docs.github.com/ru/graphql/overview/explorer


class UseGraphQL:
    """
    Формирует json запрос к GraphQL GitHub'а, отправляет через класс Link.
    :return: информацию о репозитории полученную от Link
    """
    def __init__(self, repository_owner, repository_name, cursor, token, labels_bug=None):
        """
        :param repository_owner: логин владельца репозитория
        :param repository_name: имя репозитория
        :param cursor: курсор, для последовотельного запроса данных
        :param token: токен, для получения доступа
        :param labels_bug: наименования bug меток, список
        """
        self.repository_owner = repository_owner
        self.repository_name = repository_name
        self.cursor = cursor
        self.token = token
        self.labels_bug = labels_bug

    async def get_info_labels_json(self):
        json = {
            'query':
            """
            query GetInfo ($owner: String!, $name: String!, $cursor: String) {
                repository(name: $name, owner: $owner) {                    
                    owner {
                        login
                    }
                    name
                    description                    
                    stargazerCount
                    createdAt
                    updatedAt
                    pushedAt
                    isArchived
                    isLocked
                    issues {
                        totalCount
                    }
                    watchers {
                        totalCount
                    }
                    forkCount
                    releases(first: 100) {
                        edges {
                            node {
                                publishedAt
                                tag {
                                    name
                                }
                            }
                        }
                    }
                    pullRequests(last: 100) {
                        nodes {
                            publishedAt
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
        data = await instance_link.link()
        return data

    async def get_bug_issues_json(self):
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
                                createdAt
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
        data = await instance_link.link()
        return data


class Link:
    """
    Делает запрос к GraphQL GitHub'а используя полученый json.
    В случае ошибки записывает ошибку в resp_json и возвращает None.
    :return: информацию полученную от GitHub'а в формате словаря python
    """
    def __init__(self, token, json):
        self.url = 'https://api.github.com/graphql'
        self.headers = {'Authorization': 'token ' + token}
        self.json = json

    async def link(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=self.url, headers=self.headers, json=self.json) as resp:
                    data = json.loads(await resp.read())
                return data
        except requests.exceptions.ConnectionError as e:
            logger.error(f'ERROR500! Ошибка ссоединения с сервером. Исключение: {e}')
            resp_json.query_info.code = 500
            resp_json.query_info.error_desc = 'ConnectionError'
            resp_json.query_info.error_message = str(e)
