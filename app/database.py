from analytical import github_api_client as ga
from analytical import func_api_client as fa
from app import models, db, func
from datetime import datetime
from req_response import resp_json

class DataBaseHandler:
    def get_report(self, repository_path, token, json_type='full', force=True):
        try:
            repository_path = repository_path.split('/')
            repository_path = repository_path[-2] + '/' + repository_path[-1]
        except IndexError as e:
            return fa.path_error_400(repository_path, e)





        self.repository_path = repository_path

        self.find_repository()
        # Проверка что репозиторий найден в БД и forse=False
        if self.repo_find and not force:
            # Проверка актуальности репозитория, данные в БД обновляются если с момента запроса прошло N часов
            # Количество прошедших часов (hours) должно ровняться или привышать стоимость запроса (request_cost)
            # Если времени прошло не достаточно, данные загружаются из БД
            hours = ((datetime.utcnow() - self.repo_find.upd_date)*24).days
            if hours < self.repo_find.request_cost:
                self.load_repo_data()
                return self.load_json

        instance_api_client = ga.GithubApiClient(token)
        instance_api_client.get_new_report(self.repository_path, json_type)
        if resp_json.query_info.code == 200:
            self.save_or_upd_repo_data()
            # Проверка стоимости запроса, записывать ли в статистику
            if self.return_json['queryInfo']['cost'] > 10:
                self.save_statistic()
        return self.return_json

    def save_or_upd_repo_data(self):
        self.repository_path = resp_json.repository_info.owner + '/' + resp_json.repository_info.name
        self.find_repository()
        if self.repo_find:
            self.update_repo()
        else:
            self.create_repo()

    def update_repo(self):
        self.repo_find.description = self.return_json['repositoryInfo']['description']
        self.repo_find.stars_count = self.return_json['repositoryInfo']['stars']
        self.repo_find.version = self.return_json['repositoryInfo']['version']
        self.repo_find.created_at = self.return_json['repositoryInfo']['createdAt']
        self.repo_find.duration = self.return_json['repositoryInfo']['duration']
        self.repo_find.updated_at = self.return_json['repositoryInfo']['updatedAt']
        self.repo_find.pushed_at = self.return_json['repositoryInfo']['pushedAt']
        self.repo_find.is_archived = self.return_json['repositoryInfo']['isArchived']
        self.repo_find.is_locked = self.return_json['repositoryInfo']['isLocked']
        self.repo_find.issues_count = self.return_json['repositoryInfo']['issuesCount']
        self.repo_find.bug_issues_count = self.return_json['repositoryInfo']['bugIssuesCount']
        self.repo_find.bug_issues_closed_count = self.return_json['repositoryInfo']['bugIssuesClosedCount']
        self.repo_find.bug_issues_open_count = self.return_json['repositoryInfo']['bugIssuesOpenCount']
        self.repo_find.watchers_count = self.return_json['repositoryInfo']['watchersCount']
        self.repo_find.fork_count = self.return_json['repositoryInfo']['forkCount']
        self.repo_find.closed_bug_95percent = self.return_json['analytic']['bugsClosedTime95percent']
        self.repo_find.closed_bug_50percent = self.return_json['analytic']['bugsClosedTime50percent']
        self.repo_find.upd_major_ver = self.return_json['analytic']['majorDaysPassed']
        self.repo_find.upd_minor_ver = self.return_json['analytic']['minorDaysPassed']
        self.repo_find.upd_path_ver = self.return_json['analytic']['patchDaysPassed']
        self.repo_find.bug_issues_no_comment = self.return_json['analytic']['percentIssuesNoComment']
        self.repo_find.bug_issues_closed_two_months = self.return_json['analytic']['percentIssuesClosed2months']
        self.repo_find.pr_closed_count = self.return_json['analytic']['pullRequestClosed2months']
        self.repo_find.pr_closed_duration = self.return_json['analytic']['medianDurationPullRequest']
        self.repo_find.request_time = self.return_json['queryInfo']['time']
        self.repo_find.request_cost = self.return_json['queryInfo']['cost']
        db.session.commit()

    def create_repo(self):
        repo_data = models.RepositoryInfo(
            repo_path=self.return_json['repositoryInfo']['owner'] + '/' + self.return_json['repositoryInfo']['name'],
            description=self.return_json['repositoryInfo']['description'],
            stars_count=self.return_json['repositoryInfo']['stars'],
            version=self.return_json['repositoryInfo']['version'],
            created_at=self.return_json['repositoryInfo']['createdAt'],
            duration=self.return_json['repositoryInfo']['duration'],
            updated_at=self.return_json['repositoryInfo']['updatedAt'],
            pushed_at=self.return_json['repositoryInfo']['pushedAt'],
            is_archived=self.return_json['repositoryInfo']['isArchived'],
            is_locked=self.return_json['repositoryInfo']['isLocked'],
            issues_count=self.return_json['repositoryInfo']['issuesCount'],
            bug_issues_count=self.return_json['repositoryInfo']['bugIssuesCount'],
            bug_issues_closed_count=self.return_json['repositoryInfo']['bugIssuesClosedCount'],
            bug_issues_open_count=self.return_json['repositoryInfo']['bugIssuesOpenCount'],
            watchers_count=self.return_json['repositoryInfo']['watchersCount'],
            fork_count=self.return_json['repositoryInfo']['forkCount'],
            closed_bug_95percent=self.return_json['analytic']['bugsClosedTime95percent'],
            closed_bug_50percent=self.return_json['analytic']['bugsClosedTime50percent'],
            upd_major_ver=self.return_json['analytic']['majorDaysPassed'],
            upd_minor_ver=self.return_json['analytic']['minorDaysPassed'],
            upd_path_ver=self.return_json['analytic']['patchDaysPassed'],
            bug_issues_no_comment=self.return_json['analytic']['percentIssuesNoComment'],
            bug_issues_closed_two_months=self.return_json['analytic']['percentIssuesClosed2months'],
            pr_closed_count=self.return_json['analytic']['pullRequestClosed2months'],
            pr_closed_duration=self.return_json['analytic']['medianDurationPullRequest'],
            request_time=self.return_json['queryInfo']['time'],
            request_cost=self.return_json['queryInfo']['cost'],
        )
        db.session.add(repo_data)
        db.session.commit()

    def save_statistic(self):
        request_time = float(self.return_json['queryInfo']['time'])
        request_cost = self.return_json['queryInfo']['cost']
        if self.return_json['queryInfo']['remaining'] < 3000:
            query_limit = self.return_json['queryInfo']['remaining']
        else:
            query_limit = None
        statistic = models.QueryStatistics(
            repo_path=self.return_json['repositoryInfo']['owner'] + '/' + self.return_json['repositoryInfo']['name'],
            issues_count=self.return_json['repositoryInfo']['issuesCount'],
            bug_issues_count=self.return_json['repositoryInfo']['bugIssuesCount'],
            request_time=request_time,
            request_cost=request_cost,
            request_kf=round(request_time/request_cost, 3),
            query_limit=query_limit,
            rt=self.return_json['queryInfo']['rt']
        )
        db.session.add(statistic)
        db.session.commit()

    def load_repo_data(self):
        repo_owner, repo_name = self.repo_find.repo_path.split('/', 2)
        self.load_json = {
            'repositoryInfo': {
                'name': repo_name,
                'owner': repo_owner,
                'description': self.repo_find.description,
                'stars': self.repo_find.stars_count,
                'version': self.repo_find.version,
                'createdAt': str(self.repo_find.created_at),
                'duration': self.repo_find.duration,
                'updatedAt': self.repo_find.updated_at,
                'pushedAt': self.repo_find.pushed_at,
                'isArchived': self.repo_find.is_archived,
                'isLocked': self.repo_find.is_locked,
                'issuesCount': self.repo_find.issues_count,
                'bugIssuesCount': self.repo_find.bug_issues_count,
                'bugIssuesClosedCount': self.repo_find.bug_issues_closed_count,
                'bugIssuesOpenCount': self.repo_find.bug_issues_open_count,
                'watchersCount': self.repo_find.watchers_count,
                'forkCount': self.repo_find.fork_count,
            },
            'analytic': {
                'bugsClosedTime95percent': self.repo_find.closed_bug_95percent,
                'bugsClosedTime50percent': self.repo_find.closed_bug_50percent,
                'majorDaysPassed': self.repo_find.upd_major_ver,
                'minorDaysPassed': self.repo_find.upd_minor_ver,
                'patchDaysPassed': self.repo_find.upd_path_ver,
                'percentIssuesNoComment': self.repo_find.bug_issues_no_comment,
                'percentIssuesClosed2months': self.repo_find.bug_issues_closed_two_months,
                'pullRequestClosed2months': self.repo_find.pr_closed_count,
                'medianDurationPullRequest': self.repo_find.pr_closed_duration,
            },
            'queryInfo': {
                'time': None,
                'cost': None,
                'remaining': None,
                'resetAt': None,
                'rt': None,
                'database': f'Information from the database for {str(self.repo_find.upd_date)} UTC',
                'code': 200,
            },
        }

    def find_repository(self):
        self.repo_find = models.RepositoryInfo.query.filter(
            func.lower(models.RepositoryInfo.repo_path) == self.repository_path.lower(),
        ).first()
