import sys
import re
import analytical.use_graphql as ug
import analytical.func_api_client as fa
import analytical.bug_issues as bi
from datetime import datetime
from statistics import median
import logging
logging.basicConfig(filename='../logs.log', level=logging.ERROR)


class GithubApiClient:
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
        self.bug_issues_total_count = None
        repo_owner_name = re.search('([^/]+/[^/]+)$', repository_path)
        if repo_owner_name:
            data = repo_owner_name.group(1)
            self.repository_owner, self.repository_name = data.split('/', 2)
        else:
            logging.error(f'ERR400!ok Не распознан repository_path="{repository_path}".')
            self.json_error_err400()
            return self.return_json
        self.request_total_cost = 0
        err = self.get_info_labels()
        if err == 404:
            logging.error(f'ERR404!ok Не найден репозиторий. Owner="{self.repository_owner}", '
                          f'name="{self.repository_name}".')
            return self.return_json
        self.get_bug_issues()
        self.main_analytic_unit()
        self.forming_json()
        return self.return_json

    def get_info_labels(self):
        self.cursor = None
        self.repo_version = None
        self.repo_major_version = None
        self.repo_minor_version = None
        self.repo_patch_version = None
        self.repo_pr_closed_count = None
        self.repo_pr_closed_duration = None
        self.repo_labels_name_list = []

        while True:

            data_github = ug.UseGraphQL(self.repository_owner,
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
                fa.owner_name(self.repo_owner_login, self.repo_name)
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
                    self.repo_version = self.data['data']['repository']['releases']['edges'][0]['node']['tag']['name']
                    version = fa.parsing_version(self.data['data']['repository']['releases']['edges'])
                    self.repo_major_version = version[0]
                    self.repo_minor_version = version[1]
                    self.repo_patch_version = version[2]
                if self.data['data']['repository']['pullRequests']['nodes']:
                    closed_pr = fa.pull_request_analytics(self.data['data']['repository']['pullRequests']['nodes'])
                    self.repo_pr_closed_count = closed_pr[0]
                    self.repo_pr_closed_duration = closed_pr[1]
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
            err = self.json_error_err404(err)
            if err == 404:
                return 404

    def get_bug_issues(self):
        self.cursor = None
        self.instance_b_i_a = bi.BugIssuesAnalytic()
        while True:
            data_github = ug.UseGraphQL(self.repository_owner,
                                                 self.repository_name,
                                                 self.cursor,
                                                 self.token,
                                                 self.repo_labels_bug_list)
            self.data = data_github.get_bug_issues_json()
            self.parse_bug_issues()

            if self.has_next_page:
                if not self.cursor:
                    self.bug_issues_total_count = self.data['data']['repository']['issues']['totalCount']
                    cost_multiplier = 3
                    r_time = (self.bug_issues_total_count // 100) * cost_multiplier
                    print(r_time + 5, '>', end=' ')
                self.cursor = self.end_cursor
            else:
                break

    def parse_bug_issues(self):
        self.start_cursor = self.data['data']['repository']['issues']['pageInfo']['startCursor']
        self.end_cursor = self.data['data']['repository']['issues']['pageInfo']['endCursor']
        self.has_next_page = self.data['data']['repository']['issues']['pageInfo']['hasNextPage']
        if self.data['data']['repository']['issues']['edges']:
            self.instance_b_i_a.push_bug_issues(self.data['data']['repository']['issues']['edges'])
        self.request_cost = self.data['data']['rateLimit']['cost']
        self.request_total_cost += self.request_cost
        self.request_balance = self.data['data']['rateLimit']['remaining']
        self.request_reset = self.data['data']['rateLimit']['resetAt']

    def main_analytic_unit(self):
        self.messages_info = []
        self.messages_warning = []

        bug_analytic = self.instance_b_i_a.get_bug_analytic()
        self.duration_closed_bug_min = bug_analytic[0]
        self.duration_closed_bug_max = bug_analytic[1]
        self.duration_closed_bug_95percent = bug_analytic[2]
        self.duration_closed_bug_50percent = bug_analytic[3]
        self.duration_open_bug_min = bug_analytic[4]
        self.duration_open_bug_max = bug_analytic[5]
        self.duration_open_bug_50percent = bug_analytic[6]
        self.preparation_info_data_block()
        self.preparation_badissues_data_block()
        self.analytic_repository_block()
        self.analytic_bug_issues_block()

    def preparation_info_data_block(self):
        self.repo_created_at = fa.to_date(self.repo_created_at)
        self.repo_updated_at = fa.to_date(self.repo_updated_at)
        self.repo_pushed_at = fa.to_date(self.repo_pushed_at)
        self.request_reset = fa.to_date(self.request_reset)

    def preparation_badissues_data_block(self):
        pass

    def analytic_repository_block(self):
        self.repo_duration = (datetime.now() - self.repo_created_at).days
        self.repo_updated_at = (datetime.now() - self.repo_updated_at).days
        self.repo_pushed_at = (datetime.now() - self.repo_pushed_at).days

    def analytic_bug_issues_block(self):
        pass

    def forming_json(self):
        # datetime str ???
        self.request_duration_time = datetime.now() - self.request_duration_time
        print(self.request_duration_time.seconds, end='||')
        if self.request_total_cost > 10:
            logging.error(f't_ratio_c={self.request_duration_time.seconds / self.request_total_cost} '
                          f'({self.request_total_cost}/{self.request_duration_time.seconds}) {self.repo_name}')
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
            },
            'code': 200,
        }

    def json_error_err404(self, error):
        self.return_json = {
            'errors': {
                'error': 'Repository not found',
                'type': self.data['errors'][0]['type'],
                'message': self.data['errors'][0]['message'],
            },
            'code': 404
        }
        return 404

    def json_error_err400(self):
        self.return_json = {
            'errors': {
                'error': 'Bad adress',
                'message': "Bad repository adress, enter the address in the format "
                           "'https://github.com/Vi-812/git_check_alive' or 'vi-812/git_check_alive'.",
            },
            'code': 400
        }
        return 400
