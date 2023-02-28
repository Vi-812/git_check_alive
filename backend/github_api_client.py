import backend.use_graphql as ug
import backend.func_api_client as fa
import backend.bug_issues as bi
from datetime import datetime, timedelta


class GithubApiClient:
    def __init__(self, token):
        self.token = token

    async def get_new_report(self, resp_json, repository_path, response_type='full'):
        self.resp_json = resp_json
        self.response_type = response_type  # Задействовать
        self.resp_json.meta.request_downtime = timedelta(seconds=0)
        repository_path = repository_path.split('/')
        self.repository_owner, self.repository_name = repository_path[-2], repository_path[-1]
        await self.get_info_labels()
        if resp_json.meta.code:
            return self.resp_json
        await self.get_bug_issues()
        self.resp_json = await self.instance_b_i_a.get_bug_analytic(self.resp_json)
        self.resp_json.meta.code = 200
        return self.resp_json

    async def get_info_labels(self):
        self.cursor = None
        self.repo_labels_name_list = []

        while True:
            data_github = ug.UseGraphQL(
                repository_owner=self.repository_owner,
                repository_name=self.repository_name,
                cursor=self.cursor,
                token=self.token,
            )
            self.resp_json, self.data = await data_github.get_info_labels_json(resp_json=self.resp_json)
            if self.resp_json.meta.code:
                return self.resp_json
            await self.parse_info_labels()
            if self.resp_json.meta.code:
                return self.resp_json
            if self.has_next_page:
                self.cursor = self.end_cursor
            else:
                break

        self.repo_labels_bug_list = []
        for name in self.repo_labels_name_list:
            if 'bug' in name.lower():
                self.repo_labels_bug_list.append(name)

    async def parse_info_labels(self):
        try:
            if not self.cursor:
                self.resp_json.data.owner = self.data['data']['repository']['owner']['login']
                self.resp_json.data.name = self.data['data']['repository']['name']
                self.resp_json.data.description = self.data['data']['repository']['description']
                self.resp_json.data.stars = self.data['data']['repository']['stargazerCount']
                self.resp_json.data.created_at = await fa.to_date(self.data['data']['repository']['createdAt'])
                self.resp_json.data.duration = (
                        datetime.utcnow() - self.resp_json.data.created_at
                ).days
                self.resp_json.data.updated_at = (
                        datetime.utcnow() - await fa.to_date(self.data['data']['repository']['updatedAt'])
                ).days
                self.resp_json.data.pushed_at = (
                        datetime.utcnow() - await fa.to_date(self.data['data']['repository']['pushedAt'])
                ).days
                self.resp_json.data.archived = self.data['data']['repository']['isArchived']
                self.resp_json.data.locked = self.data['data']['repository']['isLocked']
                self.resp_json.data.issues_count = self.data['data']['repository']['issues']['totalCount']
                self.resp_json.data.watchers_count = self.data['data']['repository']['watchers']['totalCount']
                self.resp_json.data.fork_count = self.data['data']['repository']['forkCount']
                if self.data['data']['repository']['releases']['edges']:
                    self.resp_json.data.version = \
                        self.data['data']['repository']['releases']['edges'][0]['node']['tag']['name']
                    self.resp_json = await fa.parsing_version(
                        resp_json=self.resp_json,
                        data=self.data['data']['repository']['releases']['edges'],
                    )
                if self.data['data']['repository']['pullRequests']['nodes']:
                    self.resp_json = await fa.pull_request_analytics(
                        resp_json=self.resp_json,
                        data=self.data['data']['repository']['pullRequests']['nodes'],
                    )
            self.start_cursor = self.data['data']['repository']['labels']['pageInfo']['startCursor']
            self.end_cursor = self.data['data']['repository']['labels']['pageInfo']['endCursor']
            self.has_next_page = self.data['data']['repository']['labels']['pageInfo']['hasNextPage']
            for label in self.data['data']['repository']['labels']['edges']:
                self.repo_labels_name_list.append(label['node']['name'])
            self.request_cost = self.data['data']['rateLimit']['cost']
            self.resp_json.meta.cost += self.request_cost
            self.resp_json.meta.remains = self.data['data']['rateLimit']['remaining']
            self.resp_json.meta.reset_at = self.data['data']['rateLimit']['resetAt']
        except (TypeError, KeyError) as e:
            if str(e) == "'data'":
                return await fa.json_error_401(
                    resp_json=self.resp_json,
                    repository_owner=self.repository_owner,
                    repository_name=self.repository_name,
                    e_data=self.data,
                )
            if str(e) == "'NoneType' object is not subscriptable":
                return await fa.json_error_404(
                    resp_json=self.resp_json,
                    repository_owner=self.repository_owner,
                    repository_name=self.repository_name,
                    error=self.data['errors'][0]['message'],
                )

    async def get_bug_issues(self):
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
            self.resp_json, self.data = await data_github.get_bug_issues_json(resp_json=self.resp_json)
            await self.parse_bug_issues()
            if not self.cursor and self.resp_json.data.bug_issues_count > 200:
                # Предварительный расчет времени запроса
                cost_multiplier = 2.9
                cost_upped = cost_multiplier * 2
                self.resp_json.meta.estimated_time = str(round(
                    ((self.resp_json.data.bug_issues_count // 100) * cost_multiplier) + cost_upped
                    , 2))
            if self.has_next_page:
                self.cursor = self.end_cursor
            else:
                break

    async def parse_bug_issues(self):
        self.resp_json.data.bug_issues_count = self.data['data']['repository']['issues']['totalCount']
        self.start_cursor = self.data['data']['repository']['issues']['pageInfo']['startCursor']
        self.end_cursor = self.data['data']['repository']['issues']['pageInfo']['endCursor']
        self.has_next_page = self.data['data']['repository']['issues']['pageInfo']['hasNextPage']
        if self.data['data']['repository']['issues']['edges']:
            await self.instance_b_i_a.push_bug_issues(self.data['data']['repository']['issues']['edges'])
        self.request_cost = self.data['data']['rateLimit']['cost']
        self.resp_json.meta.cost += self.request_cost
        self.resp_json.meta.remains = self.data['data']['rateLimit']['remaining']
        self.resp_json.meta.reset_at = self.data['data']['rateLimit']['resetAt']
