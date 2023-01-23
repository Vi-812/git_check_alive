import sys
import re
import use_graphql
from datetime import datetime, timedelta
from statistics import median
# https://developer.chrome.com/docs/devtools/network/


class GithubApiClient():
    """
    ОПИСАТЕЛЬНОЕ ОПИСАНИЕ
    """

    def __init__(self, token):
        self.token = token

    def push_repository(self, repository_path):
        """

        :param repository_path:
        :return:
        """
        self.request_duration_time = datetime.now()
        data = re.search('([^/]+/[^/]+)$', repository_path)
        if data:
            data = data.group(1)
            self.repository_owner, self.repository_name = data.split('/', 2)
        else:
            print('Ссылка не корректна, введите ссылку в формате')
            print('"https://github.com/Vi-812/git" либо "vi-812/git"')
            sys.exit()
        self.request_total_cost = 0
        self.get_info_labels()
        self.get_bug_issues()
        self.main_analytic_unit()
        self.forming_json()

    def get_info_labels(self):
        self.cursor = None
        self.repo_pullreq_publised_at_list = []
        self.repo_pullreq_last_edited_at_list = []
        self.repo_pullreq_closed_at_list = []
        self.repo_pullreq_closed_bool_list = []
        self.repo_labels_name_list = []

        while True:

            data_github = use_graphql.UseGraphQL(self.repository_owner,
                                                 self.repository_name,
                                                 self.cursor,
                                                 self.token)
            self.data = data_github.get_info_labels_json()

            self.parse_info_labels()

            if self.has_next_page:
                self.cursor = self.end_cursor
            else:
                break

        self.repo_labels_bug_list = []
        for name in self.repo_labels_name_list:
            if 'bug' in name.lower():
                self.repo_labels_bug_list.append(name)

    def parse_info_labels(self):
        try:
            self.repo_name = self.data['data']['repository']['name']
            self.repo_owner_login = self.data['data']['repository']['owner']['login']
            self.repo_description = self.data['data']['repository']['description']
            self.repo_homepage_url = self.data['data']['repository']['homepageUrl']
            self.repo_in_organization = self.data['data']['repository']['isInOrganization']
            self.repo_license_have = bool(self.data['data']['repository']['licenseInfo'])
            self.repo_stars_count = self.data['data']['repository']['stargazerCount']
            self.repo_created_at = self.data['data']['repository']['createdAt']
            self.repo_updated_at = self.data['data']['repository']['updatedAt']
            self.repo_pushed_at = self.data['data']['repository']['pushedAt']
            self.repo_is_archived_bool = self.data['data']['repository']['isArchived']
            self.repo_is_disabled_bool = self.data['data']['repository']['isDisabled']
            self.repo_is_locked_bool = self.data['data']['repository']['isLocked']
            self.repo_is_empty_bool = self.data['data']['repository']['isEmpty']
            self.repo_is_fork_bool = self.data['data']['repository']['isFork']
            self.repo_issues_total_count = self.data['data']['repository']['issues']['totalCount']
            self.repo_watchers_total_count = self.data['data']['repository']['watchers']['totalCount']
            self.repo_fork_total_count = self.data['data']['repository']['forkCount']
            for pull_r in self.data['data']['repository']['pullRequests']['nodes']:
                self.repo_pullreq_publised_at_list.append(pull_r['publishedAt'])
                self.repo_pullreq_last_edited_at_list.append(pull_r['lastEditedAt'])
                self.repo_pullreq_closed_at_list.append(pull_r['closedAt'])
                self.repo_pullreq_closed_bool_list.append(pull_r['closed'])
            self.repo_labels_total_count = self.data['data']['repository']['labels']['totalCount']
            self.start_cursor = self.data['data']['repository']['labels']['pageInfo']['startCursor']
            self.end_cursor = self.data['data']['repository']['labels']['pageInfo']['endCursor']
            self.has_next_page = self.data['data']['repository']['labels']['pageInfo']['hasNextPage']
            for label in self.data['data']['repository']['labels']['edges']:
                self.repo_labels_name_list.append(label['node']['name'])
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
        self.bug_issues_updated_at_list = []
        self.bug_issues_closed_at_list = []
        self.bug_issues_closed_bool_list = []
        self.bug_issues_comments_count_list = []
        self.bug_issues_comments_last_list = []

        while True:

            data_github = use_graphql.UseGraphQL(self.repository_owner,
                                                 self.repository_name,
                                                 self.cursor,
                                                 self.token,
                                                 self.repo_labels_bug_list)
            self.data = data_github.get_bug_issues_json()

            self.parse_bug_issues()

            if self.has_next_page:
                self.cursor = self.end_cursor
            else:
                break

    def parse_bug_issues(self):
        try:
            self.bug_issues_total_count = self.data['data']['repository']['issues']['totalCount']
            self.start_cursor = self.data['data']['repository']['issues']['pageInfo']['startCursor']
            self.end_cursor = self.data['data']['repository']['issues']['pageInfo']['endCursor']
            self.has_next_page = self.data['data']['repository']['issues']['pageInfo']['hasNextPage']
            for bug_issue in self.data['data']['repository']['issues']['edges']:
                self.bug_issues_id_list.append(bug_issue['node']['id'])
                self.bug_issues_title_list.append(bug_issue['node']['title'])
                self.bug_issues_created_at_list.append(bug_issue['node']['createdAt'])
                self.bug_issues_updated_at_list.append(bug_issue['node']['updatedAt'])
                self.bug_issues_closed_at_list.append(bug_issue['node']['closedAt'])
                self.bug_issues_closed_bool_list.append(bug_issue['node']['closed'])
                self.bug_issues_comments_count_list.append(bug_issue['node']['comments']['totalCount'])
                if bug_issue['node']['comments']['nodes']:
                    self.bug_issues_comments_last_list.append(bug_issue['node']['comments']['nodes'][0]['createdAt'])
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
        self.preparation_data_block()
        self.analytic_repository_block()
        self.analytic_bug_issues_block()







    def preparation_data_block(self):
        def to_date(date_str):
            return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
        self.repo_created_at = to_date(self.repo_created_at)
        self.repo_updated_at = to_date(self.repo_updated_at)
        self.repo_pushed_at = to_date(self.repo_pushed_at)
        self.request_reset = to_date(self.request_reset)
        self.bug_issues_open_total_count = 0
        self.bug_issues_closed_total_count = 0
        self.bug_issues_duration_all_list = []
        self.bug_issues_duration_closed_list = []
        self.bug_issues_duration_open_list = []

        list_len = len(self.repo_pullreq_publised_at_list)
        validation_list = all(map(lambda lst: len(lst) == list_len, [
            self.repo_pullreq_last_edited_at_list,
            self.repo_pullreq_closed_at_list,
            self.repo_pullreq_closed_bool_list,
        ]))
        if not validation_list:
            print('Ошибка! Несоответствие при валидации длинны массивов repo_pullreq!')
            sys.exit()
        for i in range(list_len):
            self.repo_pullreq_publised_at_list[i] = to_date(self.repo_pullreq_publised_at_list[i])
            if self.repo_pullreq_last_edited_at_list[i]:
                self.repo_pullreq_last_edited_at_list[i] = to_date(self.repo_pullreq_last_edited_at_list[i])
            if self.repo_pullreq_closed_at_list[i]:
                self.repo_pullreq_closed_at_list[i] = to_date(self.repo_pullreq_closed_at_list[i])

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
            print('Ошибка! Несоответствие при валидации длинны массивов bug_issues!')
            sys.exit()
        for i in range(list_len):
            self.bug_issues_created_at_list[i] = to_date(self.bug_issues_created_at_list[i])
            if bool(self.bug_issues_closed_at_list[i]) and self.bug_issues_closed_bool_list[i]:
                self.bug_issues_closed_total_count += 1
                self.bug_issues_closed_at_list[i] = to_date(self.bug_issues_closed_at_list[i])
                duration = self.bug_issues_closed_at_list[i] - self.bug_issues_created_at_list[i]
                self.bug_issues_duration_all_list.append(duration)
                self.bug_issues_duration_closed_list.append(duration)
            elif not bool(self.bug_issues_closed_at_list[i]) and not self.bug_issues_closed_bool_list[i]:
                self.bug_issues_open_total_count += 1
                self.bug_issues_duration_all_list.append(None)
                self.bug_issues_duration_open_list.append(datetime.now() - self.bug_issues_created_at_list[i])
            else:
                print(f'Ошибка! Несоответствие информации о закрытии issues с id = {self.bug_issues_id_list[i]}, '
                      f'closed = {self.bug_issues_closed_bool_list[i]}, '
                      f'closed_at = {self.bug_issues_closed_at_list[i]}')
                sys.exit()
            self.bug_issues_updated_at_list[i] = to_date(self.bug_issues_updated_at_list[i])
            if self.bug_issues_comments_last_list[i]:
                self.bug_issues_comments_last_list[i] = to_date(self.bug_issues_comments_last_list[i])

    def analytic_repository_block(self):
        pass
        # self.repo_duration = (datetime.now() - self.repo_created_at).days
        # self.repo_last_updated = (datetime.now() - self.repo_updated_at).days
        # print(self.repo_duration)
        # print(self.repo_last_updated)
        # FC

    def analytic_bug_issues_block(self):
        if self.bug_issues_duration_closed_list:
            self.duration_closed_bug_min = min(self.bug_issues_duration_closed_list)
            self.duration_closed_bug_max = max(self.bug_issues_duration_closed_list)
            self.duration_closed_bug_median = median(self.bug_issues_duration_closed_list)
        else:
            self.duration_closed_bug_min = timedelta(days=0)
            self.duration_closed_bug_max = timedelta(days=0)
            self.duration_closed_bug_median = timedelta(days=0)

        if self.bug_issues_duration_open_list:
            self.duration_open_bug_min = min(self.bug_issues_duration_open_list)
            self.duration_open_bug_max = max(self.bug_issues_duration_open_list)
            self.duration_open_bug_median = median(self.bug_issues_duration_open_list)
        else:
            self.duration_open_bug_min = timedelta(days=0)
            self.duration_open_bug_max = timedelta(days=0)
            self.duration_open_bug_median = timedelta(days=0)

    def forming_json(self):
        self.request_duration_time = datetime.now() - self.request_duration_time
        self.return_json = {
            'repositoryInfo': {
                'name': self.repo_name,
                'description': self.repo_description,
            },
            'queryInfo': {
                'time': str(self.request_duration_time),
                'cost': self.request_total_cost,
                'remaining': self.request_balance,
                'resetAt': str(self.request_reset),
            }
        }

    def get_json(self):
        return self.return_json
