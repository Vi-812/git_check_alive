import aiohttp
import requests
import json
from datetime import datetime
from loguru import logger
from backend.analytic import functions as fn


# Сформировать json можно тут (кнопка Explorer)
# https://docs.github.com/ru/graphql/overview/explorer


class UseGraphQL:
    """
    Формирует json запрос к GraphQL GitHub'а, отправляет через класс Link.
    :param cursor: курсор, для последовательного запроса данных
    :param repo_labels_bug_list: список bug меток
    :return: информацию о репозитории полученную от Link
    """

    async def get_info_labels_json(self, rec_request, resp_json, cursor):
        json_gql = {
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
                "owner": rec_request.repo_owner,
                "name": rec_request.repo_name,
                "cursor": cursor
            }
        }
        instance_link = Link()
        return await instance_link.link(
            rec_request=rec_request,
            resp_json=resp_json,
            json_gql=json_gql
        )

    async def get_bug_issues_json(self, rec_request, resp_json, cursor, repo_labels_bug_list):
        # issues(first: 100, filterBy: {labels: $labels, createdBy: "2018-01-01..*"}, after: $cursor) {
        json_gql = {
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
                "owner": rec_request.repo_owner,
                "name": rec_request.repo_name,
                "labels": repo_labels_bug_list,
                "cursor": cursor
            }
        }
        instance_link = Link()
        return await instance_link.link(
            rec_request=rec_request,
            resp_json=resp_json,
            json_gql=json_gql,
        )


class Link:
    """
    Делает запрос к GraphQL GitHub'а используя полученный json.
    В случае ошибки записывает ошибку в resp_json.
    :return: информацию, полученную от GitHub'а (в формате словаря python)
    """

    async def link(self, rec_request, resp_json, json_gql):
        url = 'https://api.github.com/graphql'  # Эндпоинт для запросов
        headers = {'Authorization': 'token ' + rec_request.token}  # Помещаем токен в headers
        try:
            async with aiohttp.ClientSession() as session:  # Начинаем сессию
                ght = datetime.utcnow()  # Засекаем время запроса к GraphQL
                async with session.post(url=url, headers=headers, json=json_gql) as resp:  # Формируем запрос resp
                    data = json.loads(await resp.read())  # Ожидаем ответ от resp, переводим в json
                resp_json.meta.request_downtime += datetime.utcnow() - ght  # Добавляем время в request_downtime
                if data.get('message') == 'Bad credentials':  # Обработка ошибки некорректного токена
                    return await fn.json_error_401(
                        rec_request=rec_request,
                        resp_json=resp_json,
                        e_data=data,
                    ), data
                return resp_json, data
        except requests.exceptions.ConnectionError as e:  # Обработка ошибки соединения с GitHub
            logger.error(f'E_500! Ошибка соединения с сервером, {e=}, '
                         f'rec_request={rec_request.dict(exclude={"token"})}')
            resp_json.meta.code = 500
            resp_json.error.description = 'ConnectionError'
            resp_json.error.message = str(e)
            return resp_json, data
