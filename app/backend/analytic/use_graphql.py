import json
import aiohttp
from aiohttp.client_exceptions import ClientConnectorError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from app.backend.analytic import errors_handler as eh


# Сформировать json можно тут (кнопка Explorer)
# https://docs.github.com/ru/graphql/overview/explorer


class UseGraphQL:
    """
    Формирует json запрос к GraphQL GitHub'а, отправляет через класс Link.
    :param cursor: курсор, для последовательного запроса данных
    :param repo_labels_bug_list: список bug меток
    :return: информацию о репозитории полученную от Link
    """

    def __init__(self, years=1):
        # Получаем дату актуальности данных, текущяя дата - years, переводим в isoformat
        self.since_date = (datetime.utcnow() - relativedelta(years=years)).isoformat()

        # Создаем экземпляр класса Link
        self.instance_link = Link()

    async def get_info_labels_json(self, rec_request, resp_json, cursor):
        json_gql = {  # Формируем запрос к GitHub
            'query':
            """
            query GetInfo ($owner: String!, $name: String!, $date: DateTime!, $cursor: String) {
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
                    issues(first: 1, filterBy: {since: $date}) {
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
            'variables': {  # Переменные
                "owner": rec_request.repo_owner,
                "name": rec_request.repo_name,
                "date": self.since_date,
                "cursor": cursor,
            }
        }
        return await self.instance_link.link(
            rec_request=rec_request,
            resp_json=resp_json,
            json_gql=json_gql
        )

    async def get_bug_issues_json(self, rec_request, resp_json, cursor, repo_labels_bug_list):
        json_gql = {  # Формируем запрос к GitHub
            'query':
            """
            query GetIssues($owner: String!, $name: String!, $labels: [String!], $date: DateTime!, $cursor: String) {
                repository(name: $name, owner: $owner) {
                    issues(first: 100, filterBy: {labels: $labels, since: $date}, after: $cursor) {
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
            'variables': {  # Переменные
                "owner": rec_request.repo_owner,
                "name": rec_request.repo_name,
                "labels": repo_labels_bug_list,
                "date": self.since_date,
                "cursor": cursor,
            }
        }
        return await self.instance_link.link(
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
                ght = datetime.utcnow()  # Засекаем время запроса к GraphQL (для request_downtime)
                async with session.post(url=url, headers=headers, json=json_gql) as resp:  # Формируем запрос resp
                    github_data = json.loads(await resp.read())  # Ожидаем ответ от resp, переводим в json
                resp_json.meta.request_downtime += datetime.utcnow() - ght  # Добавляем время в request_downtime
                if github_data.get('message') == 'Bad credentials':  # Обработка ошибки некорректного токена
                    return await eh.json_error_401(
                        rec_request=rec_request,
                        resp_json=resp_json,
                        e_data=github_data,
                    ), github_data
                return resp_json, github_data
        except ClientConnectorError as e:  # Обработка ошибки соединения с GitHub
            return await eh.connection_error_500(rec_request=rec_request, resp_json=resp_json, error=e), None
        except Exception as e:  # Обработка ошибок GitHub
            return await eh.connection_error_500(rec_request=rec_request, resp_json=resp_json, error=e), None
