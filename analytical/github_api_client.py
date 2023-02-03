import analytical.use_graphql as ug
import analytical.func_api_client as fa
import analytical.bug_issues as bi
from datetime import datetime
from app import logger
from req_response import resp_json


class GithubApiClient:
    def __init__(self, token):
        self.token = token

    def get_new_report(self, repository_path, response_type='full'):
        self.response_duration_time = datetime.now()
        self.response_type = response_type
        try:
            repository_path = repository_path.split('/')
            self.repository_owner, self.repository_name = repository_path[-2], repository_path[-1]
        except IndexError as e:
            return fa.path_error_400(repository_path, e)
        self.get_info_labels()
        if resp_json.query_info.code:
            return
        self.get_bug_issues()
        self.main_analytic_unit()
        self.forming_json()

    def get_info_labels(self):
        self.cursor = None
        self.repo_labels_name_list = []

        while True:
            data_github = ug.UseGraphQL(
                self.repository_owner,
                self.repository_name,
                self.cursor,
                self.token,
            )
            self.data = data_github.get_info_labels_json()
            if resp_json.query_info.code:
                return
            self.parse_info_labels()
            if resp_json.query_info.code:
                return
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
                resp_json.repository_info.owner = self.data['data']['repository']['owner']['login']
                resp_json.repository_info.name = self.data['data']['repository']['name']
                resp_json.repository_info.description = self.data['data']['repository']['description']
                resp_json.repository_info.stars = self.data['data']['repository']['stargazerCount']
                resp_json.repository_info.created_at = fa.to_date(self.data['data']['repository']['createdAt'])
                resp_json.repository_info.duration = \
                    (datetime.now() - resp_json.repository_info.created_at).days
                resp_json.repository_info.updated_at = \
                    (datetime.now() - fa.to_date(self.data['data']['repository']['updatedAt'])).days
                resp_json.repository_info.pushed_at = \
                    (datetime.now() - fa.to_date(self.data['data']['repository']['pushedAt'])).days
                resp_json.repository_info.archived = self.data['data']['repository']['isArchived']
                resp_json.repository_info.locked = self.data['data']['repository']['isLocked']
                resp_json.repository_info.issues_count = self.data['data']['repository']['issues']['totalCount']
                resp_json.repository_info.watchers_count = self.data['data']['repository']['watchers']['totalCount']
                resp_json.repository_info.fork_count = self.data['data']['repository']['forkCount']
                if self.data['data']['repository']['releases']['edges']:
                    resp_json.repository_info.version = self.data['data']['repository']['releases']['edges'][0]['node']['tag']['name']
                    fa.parsing_version(self.data['data']['repository']['releases']['edges'])
                if self.data['data']['repository']['pullRequests']['nodes']:
                    fa.pull_request_analytics(self.data['data']['repository']['pullRequests']['nodes'])
            self.start_cursor = self.data['data']['repository']['labels']['pageInfo']['startCursor']
            self.end_cursor = self.data['data']['repository']['labels']['pageInfo']['endCursor']
            self.has_next_page = self.data['data']['repository']['labels']['pageInfo']['hasNextPage']
            for label in self.data['data']['repository']['labels']['edges']:
                self.repo_labels_name_list.append(label['node']['name'])
            self.request_cost = self.data['data']['rateLimit']['cost']
            resp_json.query_info.cost += self.request_cost
            resp_json.query_info.remains = self.data['data']['rateLimit']['remaining']
            resp_json.query_info.reset_at = self.data['data']['rateLimit']['resetAt']
        except (TypeError, KeyError) as e:
            if str(e) == "'data'":
                fa.json_error_401(self.repository_owner, self.repository_name, self.data)
            if str(e) == "'NoneType' object is not subscriptable":
                fa.json_error_404(self.repository_owner, self.repository_name, self.data['errors'][0]['message'])



    def get_bug_issues(self):
        self.cursor = None
        self.instance_b_i_a = bi.BugIssuesAnalytic()

        while True:
            data_github = ug.UseGraphQL(
                self.repository_owner,
                self.repository_name,
                self.cursor,
                self.token,
                self.repo_labels_bug_list,
            )
            self.data = data_github.get_bug_issues_json()
            self.parse_bug_issues()
            if not self.cursor and resp_json.repository_info.bug_issues_count > 200:
                # Предварительный расчет времени запроса
                cost_multiplier = 2.9
                cost_upped = cost_multiplier * 2
                resp_json.query_info.rt = \
                    str(round(((resp_json.repository_info.bug_issues_count // 100) * cost_multiplier) + cost_upped, 2))
            if self.has_next_page:
                self.cursor = self.end_cursor
            else:
                break

    def parse_bug_issues(self):
        resp_json.repository_info.bug_issues_count = self.data['data']['repository']['issues']['totalCount']
        self.start_cursor = self.data['data']['repository']['issues']['pageInfo']['startCursor']
        self.end_cursor = self.data['data']['repository']['issues']['pageInfo']['endCursor']
        self.has_next_page = self.data['data']['repository']['issues']['pageInfo']['hasNextPage']
        if self.data['data']['repository']['issues']['edges']:
            self.instance_b_i_a.push_bug_issues(self.data['data']['repository']['issues']['edges'])
        self.request_cost = self.data['data']['rateLimit']['cost']
        resp_json.query_info.cost += self.request_cost
        resp_json.query_info.remains = self.data['data']['rateLimit']['remaining']
        resp_json.query_info.reset_at = self.data['data']['rateLimit']['resetAt']

    def main_analytic_unit(self):
        self.instance_b_i_a.get_bug_analytic()

    def forming_json(self):
        self.response_duration_time = datetime.now() - self.response_duration_time
        resp_json.query_info.time = round(self.response_duration_time.seconds +
                                           (self.response_duration_time.microseconds*0.000001), 2)
        if resp_json.query_info.rt:
            resp_json.query_info.rt += '/' + str(resp_json.query_info.time)
        resp_json.query_info.code = 200
