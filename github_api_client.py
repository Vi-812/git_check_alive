import sys
import re
import json
import use_graphql
import func_api_client as fa
from datetime import datetime
from statistics import median
# https://developer.chrome.com/docs/devtools/network/


class GithubApiClient():
    """
    ОПИСАТЕЛЬНОЕ ОПИСАНИЕ
    """

    def __init__(self, token):
        self.token = token

    def get_report(self, repository_path):
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
        err = self.get_info_labels()
        if err == 404:
            return self.return_json
        self.get_bug_issues()
        self.main_analytic_unit()
        self.forming_json()
        return self.return_json

    def get_info_labels(self):
        self.cursor = None
        self.repo_major_version = None
        self.repo_minor_version = None
        self.repo_patch_version = None
        self.repo_pullrequests = {
            'published_at': [],
            'last_edited_at': [],
            'closed_at': [],
            'closed_bool': [],
        }
        self.repo_labels_name_list = []

        while True:

            data_github = use_graphql.UseGraphQL(self.repository_owner,
                                                 self.repository_name,
                                                 self.cursor,
                                                 self.token)
            self.data = data_github.get_info_labels_json()

            err = self.parse_info_labels()
            if err == 404:
                return 404

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
            if not self.cursor:
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
                self.repo_labels_total_count = self.data['data']['repository']['labels']['totalCount']
                if self.data['data']['repository']['releases']['edges']:
                    version = fa.parsing_version(self.data['data']['repository']['releases']['edges'])
                    self.repo_major_version = version[0]
                    self.repo_minor_version = version[1]
                    self.repo_patch_version = version[2]
                for pull_r in self.data['data']['repository']['pullRequests']['nodes']:
                    self.repo_pullrequests['published_at'].append(pull_r['publishedAt'])
                    self.repo_pullrequests['last_edited_at'].append(pull_r['lastEditedAt'])
                    self.repo_pullrequests['closed_at'].append(pull_r['closedAt'])
                    self.repo_pullrequests['closed_bool'].append(pull_r['closed'])
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
            err = self.json_error(err)
            if err == 404:
                return 404
        except KeyError as err:
            print('--------------------------------------------------------------')
            print('При получении данных из репозитория возникла ошибка')
            print('Ошибка при обращении по ключу')
            print(f'Ключ: {err}')
            sys.exit()

    def get_bug_issues(self):
        self.cursor = None
        self.bug_issues = {
            'id': [],
            'title': [],
            'created_at': [],
            'updated_at': [],
            'closed_at': [],
            'closed_bool': [],
            'comments_count': [],
            'comments_last': [],
        }

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
                self.bug_issues['id'].append(bug_issue['node']['id'])
                self.bug_issues['title'].append(bug_issue['node']['title'])
                self.bug_issues['created_at'].append(bug_issue['node']['createdAt'])
                self.bug_issues['updated_at'].append(bug_issue['node']['updatedAt'])
                self.bug_issues['closed_at'].append(bug_issue['node']['closedAt'])
                self.bug_issues['closed_bool'].append(bug_issue['node']['closed'])
                self.bug_issues['comments_count'].append(bug_issue['node']['comments']['totalCount'])
                if bug_issue['node']['comments']['nodes']:
                    self.bug_issues['comments_last'].append(bug_issue['node']['comments']['nodes'][0]['createdAt'])
                else:
                    self.bug_issues['comments_last'].append(None)
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
        self.preparation_info_data_block()
        self.preparation_badissues_data_block()
        self.analytic_repository_block()
        self.analytic_bug_issues_block()

    def preparation_info_data_block(self):
        self.repo_created_at = fa.to_date(self.repo_created_at)
        self.repo_updated_at = fa.to_date(self.repo_updated_at)
        self.repo_pushed_at = fa.to_date(self.repo_pushed_at)
        self.request_reset = fa.to_date(self.request_reset)
        self.bug_issues_open_total_count = 0
        self.bug_issues_closed_total_count = 0
        self.bug_issues_duration_all_list = []
        self.bug_issues_duration_closed_list = []
        self.bug_issues_duration_open_list = []
        list_len = len(self.repo_pullrequests['published_at'])
        validation_list = all(map(lambda lst: len(lst) == list_len, [
            self.repo_pullrequests['last_edited_at'],
            self.repo_pullrequests['closed_at'],
            self.repo_pullrequests['closed_bool'],
        ]))
        if not validation_list:
            print('Ошибка! Несоответствие при валидации длинны массивов "repo_pullrequests"!')
            sys.exit()
        for i in range(list_len):
            self.repo_pullrequests['published_at'][i] = fa.to_date(self.repo_pullrequests['published_at'][i])
            if self.repo_pullrequests['last_edited_at'][i]:
                self.repo_pullrequests['last_edited_at'][i] = fa.to_date(self.repo_pullrequests['last_edited_at'][i])
            if self.repo_pullrequests['closed_at'][i]:
                self.repo_pullrequests['closed_at'][i] = fa.to_date(self.repo_pullrequests['closed_at'][i])

        list_len = len(self.bug_issues['id'])
        validation_list = all(map(lambda lst: len(lst) == list_len, [
            self.bug_issues['title'],
            self.bug_issues['created_at'],
            self.bug_issues['updated_at'],
            self.bug_issues['closed_at'],
            self.bug_issues['closed_bool'],
            self.bug_issues['comments_count'],
            self.bug_issues['comments_last'],
        ]))
        if not validation_list:
            print('Ошибка! Несоответствие при валидации длинны массивов bug_issues!')
            sys.exit()
        for i in range(list_len):
            self.bug_issues['created_at'][i] = fa.to_date(self.bug_issues['created_at'][i])
            if bool(self.bug_issues['closed_at'][i]) and self.bug_issues['closed_bool'][i]:
                self.bug_issues_closed_total_count += 1
                self.bug_issues['closed_at'][i] = fa.to_date(self.bug_issues['closed_at'][i])
                duration = self.bug_issues['closed_at'][i] - self.bug_issues['created_at'][i]
                self.bug_issues_duration_all_list.append(duration)
                self.bug_issues_duration_closed_list.append(duration)
            elif not bool(self.bug_issues['closed_at'][i]) and not self.bug_issues['closed_bool'][i]:
                self.bug_issues_open_total_count += 1
                self.bug_issues_duration_all_list.append(None) # ??? --------------------------------
                self.bug_issues_duration_open_list.append(datetime.now() - self.bug_issues['created_at'][i])
            else:
                print(f'Ошибка! Несоответствие информации о закрытии issues с id = {self.bug_issues["id"][i]}, '
                      f'closed = {self.bug_issues["closed_bool"][i]}, '
                      f'closed_at = {self.bug_issues["closed_at"][i]}')
                sys.exit()
            self.bug_issues['updated_at'][i] = fa.to_date(self.bug_issues['updated_at'][i])
            if self.bug_issues['comments_last'][i]:
                self.bug_issues['comments_last'][i] = fa.to_date(self.bug_issues['comments_last'][i])

    def preparation_badissues_data_block(self):
        pass

    def analytic_repository_block(self):
        self.repo_duration = (datetime.now() - self.repo_created_at).days
        self.repo_last_updated = (datetime.now() - self.repo_updated_at).days
        self.repo_pushed_at = (datetime.now() - self.repo_pushed_at).days

    def analytic_bug_issues_block(self):
        closed_list_len = len(self.bug_issues_duration_closed_list)
        open_list_len = len(self.bug_issues_duration_open_list)
        if closed_list_len >= 10:
            self.bug_issues_duration_closed_list.sort()
            self.duration_closed_bug_min = self.bug_issues_duration_closed_list[0]
            self.duration_closed_bug_max = self.bug_issues_duration_closed_list[-1]
            self.duration_closed_bug_95percent = self.bug_issues_duration_closed_list[round((closed_list_len - 1)
                                                                                            * 0.95)].days
            self.duration_closed_bug_50percent = median(self.bug_issues_duration_closed_list).days
        else:
            self.duration_closed_bug_min = None
            self.duration_closed_bug_max = None
            self.duration_closed_bug_95percent = None
            self.duration_closed_bug_50percent = None

        if open_list_len >= 10:
            self.bug_issues_duration_open_list.sort()
            self.duration_open_bug_min = self.bug_issues_duration_open_list[0]
            self.duration_open_bug_max = self.bug_issues_duration_open_list[-1]
            self.duration_open_bug_95percent = self.bug_issues_duration_open_list[round((open_list_len - 1)
                                                                                        * 0.95)].days
            self.duration_open_bug_50percent = median(self.bug_issues_duration_open_list).days
        else:
            self.duration_open_bug_min = None
            self.duration_open_bug_max = None
            self.duration_open_bug_95percent = None
            self.duration_open_bug_50percent = None

    def forming_json(self):
        # datetime str ???
        self.request_duration_time = datetime.now() - self.request_duration_time
        self.return_json = {
            'repositoryInfo': {
                'name': self.repo_name,
                'owner': self.repo_owner_login,
            },
            'parameters': {
                'isArchived': self.repo_is_archived_bool,
                'bugsClosedTime95percent': self.duration_closed_bug_95percent,
                'bugsClosedTime50percent': self.duration_closed_bug_50percent,
                'stars': self.repo_stars_count,
                'majorDaysPassed': self.repo_major_version,
                'minorDaysPassed': self.repo_minor_version,
                'patchDaysPassed': self.repo_patch_version,
                'pushedAt': self.repo_pushed_at,
            },
            'queryInfo': {
                'time': str(self.request_duration_time),
                'cost': self.request_total_cost,
                'remaining': self.request_balance,
                'resetAt': str(self.request_reset),
            }
        }
        self.return_json = json.dumps(self.return_json)

    def json_error(self, error):
        self.return_json = {
            'errors': {
                'error': 'Repository not found',
                'type': self.data['errors'][0]['type'],
                'message': self.data['errors'][0]['message'],
            }
        }
        return 404
