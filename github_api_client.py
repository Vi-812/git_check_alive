import sys
import use_graphql
from datetime import datetime, timedelta
from statistics import median
# https://developer.chrome.com/docs/devtools/network/


class GithubApiClient():
    """
    ОПИСАТЕЛЬНОЕ ОПИСАНИЕ
    """

    def __init__(self, token):
        self.request_duration_time = datetime.now()
        self.token = token
        self.request_total_cost = 0

    def push_repository(self, repository_owner, repository_name):
        self.repository_owner = repository_owner
        self.repository_name = repository_name
        self.get_info_labels()

    def get_info_labels(self):
        self.cursor = None
        self.repo_labels_name = []

        while True:

            data_github = use_graphql.UseGraphQL(self.repository_owner, self.repository_name, self.cursor, self.token)
            self.data = data_github.get_info_labels_json()

            self.parse_info_labels()

            if self.has_next_page:
                self.cursor = self.end_cursor
            else:
                break

        self.labels_bug = []
        for name in self.repo_labels_name:
            if 'bug' in name.lower():
                self.labels_bug.append(name)
        self.get_bug_issues()

    def parse_info_labels(self):
        try:
            self.repo_name = self.data['data']['repository']['name']
            self.repo_description = self.data['data']['repository']['description']
            self.repo_stars = self.data['data']['repository']['stargazerCount']
            self.repo_created_at = self.data['data']['repository']['createdAt']
            self.repo_updated_at = self.data['data']['repository']['updatedAt']
            self.repo_archived_bool = self.data['data']['repository']['isArchived']
            self.repo_issues_total_count = self.data['data']['repository']['issues']['totalCount']
            self.repo_labels_count = self.data['data']['repository']['labels']['totalCount']
            self.start_cursor = self.data['data']['repository']['labels']['pageInfo']['startCursor']
            self.end_cursor = self.data['data']['repository']['labels']['pageInfo']['endCursor']
            self.has_next_page = self.data['data']['repository']['labels']['pageInfo']['hasNextPage']
            for label in self.data['data']['repository']['labels']['edges']:
                self.repo_labels_name.append(label['node']['name'])
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
        # except KeyError as err:
        #     print('--------------------------------------------------------------')
        #     print('При получении данных из репозитория возникла ошибка')
        #     print('Ошибка при обращении по ключу')
        #     print(f'Ключ: {err}')
        #     sys.exit()

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

            data_github = use_graphql.UseGraphQL(self.repository_owner, self.repository_name, self.cursor, self.token, self.labels_bug)
            self.data = data_github.get_bug_issues_json()

            self.parse_bug_issues()

            if self.has_next_page:
                self.cursor = self.end_cursor
            else:
                break
        self.main_analytic_unit()

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

    def main_analytic_unit(self):
        self.messages_info = []
        self.messages_warning = []
        self.data_preparation_block()
        self.repository_analytic_block()



        self.forming_json()

    def data_preparation_block(self):
        def to_date(date_str):
            return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
        self.repo_created_at = to_date(self.repo_created_at)
        self.repo_updated_at = to_date(self.repo_updated_at)
        self.request_reset = to_date(self.request_reset)
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
            print('Ошибка! Несоответствие при валидации длинны массивов!')
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

    def repository_analytic_block(self):
        self.repo_duration = (datetime.now() - self.repo_created_at).days
        self.repo_last_updated = (datetime.now() - self.repo_updated_at).days
        print(self.repo_duration)
        print(self.repo_last_updated)

    def forming_json(self):
        self.request_duration_time = datetime.now() - self.request_duration_time
        self.return_json = {
            'repositoryInfo': {
                'name': self.repo_name,
                'description': self.repo_description,
            },
            'queryInfo': {
                'time': self.request_duration_time,
                'cost': self.request_total_cost,
                'remaining': self.request_balance,
                'resetAt': self.request_reset,
            }
        }

    def get_json(self):
        return self.return_json
