import requests
import sys
import os
import json
from datetime import datetime, timedelta
from statistics import median
from json_file import get_info_labels_json, get_bug_issues_json
from dotenv import load_dotenv
load_dotenv()

# https://developer.chrome.com/docs/devtools/network/


class GitGraphql():
    """
    ОПИСАТЕЛЬНОЕ ОПИСАНИЕ
    """

    def __init__(self, repository_owner, repository_name):
        self.request_duration_time = datetime.now()
        self.url = 'https://api.github.com/graphql'
        self.headers = {'Authorization': 'token ' + os.getenv('TOKEN')}
        self.repository_owner = repository_owner
        self.repository_name = repository_name
        self.request_total_cost = 0


    def get_info_labels(self):
        self.cursor = None
        self.repo_labels_name = []

        while True:

            self.json = get_info_labels_json(self.repository_owner, self.repository_name, self.cursor)

            try:
                data = requests.post(url=self.url, headers=self.headers, json=self.json)
                self.data = data.json()
            except requests.exceptions.ConnectionError as err:
                print('--------------------------------------------------------------')
                print('Ошибка ссоединения с сервером')
                print(f'Исключение: {err}')
                sys.exit()

            self.parse_info_labels()

            if self.has_next_page:
                self.cursor = self.end_cursor
            else:
                break

        self.labels_bug = []
        for name in self.repo_labels_name:
            if 'bug' in name.lower():
                self.labels_bug.append(name)

    def parse_info_labels(self):
        try:
            self.repo_name = self.data['data']['repository']['name']
            self.repo_description = self.data['data']['repository']['description']
            self.repo_stars = self.data['data']['repository']['stargazerCount']
            self.repo_created_at = self.data['data']['repository']['createdAt']
            self.repo_updated_at = self.data['data']['repository']['updatedAt']
            self.repo_archived_bool = self.data['data']['repository']['isArchived']
            self.repo_labels_count = self.data['data']['repository']['labels']['totalCount']
            self.start_cursor = self.data['data']['repository']['labels']['pageInfo']['startCursor']
            self.end_cursor = self.data['data']['repository']['labels']['pageInfo']['endCursor']
            self.has_next_page = self.data['data']['repository']['labels']['pageInfo']['hasNextPage']
            for label in self.data['data']['repository']['labels']['edges']:
                self.repo_labels_name.append(label['node']['name'])
            self.repo_issues_total_count = self.data['data']['repository']['issues']['totalCount']
            self.request_cost = self.data['data']['rateLimit']['cost']
            self.request_total_cost += self.request_cost
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
        self.cursor = None
        self.bug_issues_id_list = []
        self.bug_issues_title_list = []
        self.bug_issues_created_at_list = []
        self.bug_issues_closed_at_list = []
        self.bug_issues_closed_bool_list = []
        self.bug_issues_updated_at_list = []
        self.bug_issues_comments_count_list = []
        self.bug_issues_comments_last_list = []

        while True:

            self.json = get_bug_issues_json(self.repository_owner, self.repository_name, self.labels_bug, self.cursor)

            try:
                data = requests.post(url=self.url, headers=self.headers, json=self.json)
                self.data = data.json()
            except requests.exceptions.ConnectionError as err:
                print('--------------------------------------------------------------')
                print('Ошибка ссоединения с сервером')
                print(f'Исключение: {err}')
                sys.exit()

            self.parse_bug_issues()

            if self.has_next_page:
                self.cursor = self.end_cursor
            else:
                break

    def parse_bug_issues(self):
        try:
            self.issues_bug_count = self.data['data']['repository']['issues']['totalCount']
            self.start_cursor = self.data['data']['repository']['issues']['pageInfo']['startCursor']
            self.end_cursor = self.data['data']['repository']['issues']['pageInfo']['endCursor']
            self.has_next_page = self.data['data']['repository']['issues']['pageInfo']['hasNextPage']
            for issue in self.data['data']['repository']['issues']['edges']:
                self.bug_issues_id_list.append(issue['node']['id'])
                self.bug_issues_title_list.append(issue['node']['title'])
                self.bug_issues_created_at_list.append(issue['node']['createdAt'])
                self.bug_issues_closed_at_list.append(issue['node']['closedAt'])
                self.bug_issues_closed_bool_list.append(issue['node']['closed'])
                self.bug_issues_updated_at_list.append(issue['node']['updatedAt'])
                self.bug_issues_comments_count_list.append(issue['node']['comments']['totalCount'])
                if issue['node']['comments']['nodes']:
                    self.bug_issues_comments_last_list.append(issue['node']['comments']['nodes'][0]['createdAt'])
                else:
                    self.bug_issues_comments_last_list.append(None)
            self.request_cost = self.data['data']['rateLimit']['cost']
            self.request_total_cost += self.request_cost
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

    def analyz_bug_issues(self):
        def to_date(date_str):
            return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
        self.repo_created_at = to_date(self.repo_created_at)
        self.repo_updated_at = to_date(self.repo_updated_at)
        self.issues_open_count = 0
        self.issues_closed_count = 0
        self.duration_all_bug_list = []
        self.duration_closed_bug_list = []
        self.duration_open_bug_list = []
        list_len = len(self.bug_issues_id_list)
        validation_list = all(map(lambda lst: len(lst) == list_len, [
            self.bug_issues_title_list,
            self.bug_issues_created_at_list,
            self.bug_issues_closed_at_list,
            self.bug_issues_closed_bool_list,
            self.bug_issues_updated_at_list,
            self.bug_issues_comments_count_list,
            self.bug_issues_comments_last_list,
        ]))
        if not validation_list:
            print(f'Ошибка! Несоответствие при валидации длинны массивов!')
            sys.exit()
        for i in range(list_len):
            self.bug_issues_created_at_list[i] = to_date(self.bug_issues_created_at_list[i])
            if bool(self.bug_issues_closed_at_list[i]) and self.bug_issues_closed_bool_list[i]:
                self.issues_closed_count += 1
                self.bug_issues_closed_at_list[i] = to_date(self.bug_issues_closed_at_list[i])
                duration = self.bug_issues_closed_at_list[i] - self.bug_issues_created_at_list[i]
                self.duration_all_bug_list.append(duration)
                self.duration_closed_bug_list.append(duration)
            elif not bool(self.bug_issues_closed_at_list[i]) and not self.bug_issues_closed_bool_list[i]:
                self.issues_open_count += 1
                self.duration_all_bug_list.append(None)
                self.duration_open_bug_list.append(datetime.now() - self.bug_issues_created_at_list[i])
            else:
                print(f'Ошибка! Несоответствие информации о закрытии issues с id = {self.bug_issues_id_list[i]}, '
                      f'closed = {self.bug_issues_closed_bool_list[i]}, '
                      f'closed_at = {self.bug_issues_closed_at_list[i]}')
                sys.exit()
            self.bug_issues_updated_at_list[i] = to_date(self.bug_issues_updated_at_list[i])
            if self.bug_issues_comments_last_list[i]:
                self.bug_issues_comments_last_list[i] = to_date(self.bug_issues_comments_last_list[i])

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

    def get_json(self):
        self.request_duration_time = datetime.now() - self.request_duration_time
