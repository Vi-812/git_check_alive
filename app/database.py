from analytical import github_api_client as ga
from analytical import func_api_client as fa
from app import models, db, func
from datetime import datetime
from req_response import resp_json, reset_resp_json


class DataBaseHandler:
    def get_report(self, repository_path, token, response_type='full', force=True):
        reset_resp_json()
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
            if hours < self.repo_find.cost:
                self.load_repo_data()
                return

        instance_api_client = ga.GithubApiClient(token)
        instance_api_client.get_new_report(self.repository_path, response_type)
        if resp_json.query_info.code == 200:
            self.save_or_upd_repo_data()
            # Проверка стоимости запроса, записывать ли в статистику
            if resp_json.query_info.cost > 10:
                self.save_statistic()

    def save_or_upd_repo_data(self):
        self.repository_path = resp_json.repository_info.owner + '/' + resp_json.repository_info.name
        self.find_repository()
        if self.repo_find:
            self.update_repo()
        else:
            self.create_repo()

    def update_repo(self):
        self.repo_find.description = resp_json.repository_info.description
        self.repo_find.stars = resp_json.repository_info.stars
        self.repo_find.version = resp_json.repository_info.version
        self.repo_find.created_at = resp_json.repository_info.created_at
        self.repo_find.duration = resp_json.repository_info.duration
        self.repo_find.updated_at = resp_json.repository_info.updated_at
        self.repo_find.pushed_at = resp_json.repository_info.pushed_at
        self.repo_find.archived = resp_json.repository_info.archived
        self.repo_find.locked = resp_json.repository_info.locked
        self.repo_find.issues_count = resp_json.repository_info.issues_count
        self.repo_find.bug_issues_count = resp_json.repository_info.bug_issues_count
        self.repo_find.bug_issues_closed_count = resp_json.repository_info.bug_issues_closed_count
        self.repo_find.bug_issues_open_count = resp_json.repository_info.bug_issues_open_count
        self.repo_find.watchers_count = resp_json.repository_info.watchers_count
        self.repo_find.fork_count = resp_json.repository_info.fork_count
        self.repo_find.closed_bug_95perc = resp_json.analytic.closed_bug_95perc
        self.repo_find.closed_bug_50perc = resp_json.analytic.closed_bug_50perc
        self.repo_find.upd_major_ver = resp_json.analytic.upd_major_ver
        self.repo_find.upd_minor_ver = resp_json.analytic.upd_minor_ver
        self.repo_find.upd_patch_ver = resp_json.analytic.upd_patch_ver
        self.repo_find.bug_issues_no_comment = resp_json.analytic.bug_issues_no_comment
        self.repo_find.bug_issues_closed_2months = resp_json.analytic.bug_issues_closed_2months
        self.repo_find.pr_closed_count = resp_json.analytic.pr_closed_count
        self.repo_find.pr_closed_duration = resp_json.analytic.pr_closed_duration
        self.repo_find.time = resp_json.query_info.time
        self.repo_find.cost = resp_json.query_info.cost
        db.session.commit()

    def create_repo(self):
        repo_data = models.RepositoryInfo(
            repo_path=resp_json.repository_info.owner + '/' + resp_json.repository_info.name,
            description=resp_json.repository_info.description,
            stars=resp_json.repository_info.stars,
            version=resp_json.repository_info.version,
            created_at=resp_json.repository_info.created_at,
            duration=resp_json.repository_info.duration,
            updated_at=resp_json.repository_info.updated_at,
            pushed_at=resp_json.repository_info.pushed_at,
            archived=resp_json.repository_info.archived,
            locked=resp_json.repository_info.locked,
            issues_count=resp_json.repository_info.issues_count,
            bug_issues_count=resp_json.repository_info.bug_issues_count,
            bug_issues_closed_count=resp_json.repository_info.bug_issues_closed_count,
            bug_issues_open_count=resp_json.repository_info.bug_issues_open_count,
            watchers_count=resp_json.repository_info.watchers_count,
            fork_count=resp_json.repository_info.fork_count,
            closed_bug_95perc=resp_json.analytic.closed_bug_95perc,
            closed_bug_50perc=resp_json.analytic.closed_bug_50perc,
            upd_major_ver=resp_json.analytic.upd_major_ver,
            upd_minor_ver=resp_json.analytic.upd_minor_ver,
            upd_patch_ver=resp_json.analytic.upd_patch_ver,
            bug_issues_no_comment=resp_json.analytic.bug_issues_no_comment,
            bug_issues_closed_2months=resp_json.analytic.bug_issues_closed_2months,
            pr_closed_count=resp_json.analytic.pr_closed_count,
            pr_closed_duration=resp_json.analytic.pr_closed_duration,
            time=resp_json.query_info.time,
            cost=resp_json.query_info.cost,
        )
        db.session.add(repo_data)
        db.session.commit()

    def save_statistic(self):
        time = resp_json.query_info.time
        cost = resp_json.query_info.cost
        if resp_json.query_info.remains < 3000:
            query_limit = resp_json.query_info.remains
        else:
            query_limit = None
        statistic = models.QueryStatistics(
            repo_path=resp_json.repository_info.owner + '/' + resp_json.repository_info.name,
            issues_count=resp_json.repository_info.issues_count,
            bug_issues_count=resp_json.repository_info.bug_issues_count,
            time=time,
            cost=cost,
            request_kf=round(time/cost, 3),
            query_limit=query_limit,
            rt=resp_json.query_info.rt
        )
        db.session.add(statistic)
        db.session.commit()

    def load_repo_data(self):
        resp_json.repository_info.owner, resp_json.repository_info.name = self.repo_find.repo_path.split('/', 2)
        resp_json.repository_info.description = self.repo_find.description
        resp_json.repository_info.stars = self.repo_find.stars
        resp_json.repository_info.version = self.repo_find.version
        resp_json.repository_info.created_at = self.repo_find.created_at
        resp_json.repository_info.duration = self.repo_find.duration
        resp_json.repository_info.updated_at = self.repo_find.updated_at
        resp_json.repository_info.pushed_at = self.repo_find.pushed_at
        resp_json.repository_info.archived = self.repo_find.archived
        resp_json.repository_info.locked = self.repo_find.locked
        resp_json.repository_info.issues_count = self.repo_find.issues_count
        resp_json.repository_info.bug_issues_count = self.repo_find.bug_issues_count
        resp_json.repository_info.bug_issues_closed_count = self.repo_find.bug_issues_closed_count
        resp_json.repository_info.bug_issues_open_count = self.repo_find.bug_issues_open_count
        resp_json.repository_info.watchers_count = self.repo_find.watchers_count
        resp_json.repository_info.fork_count = self.repo_find.fork_count
        resp_json.analytic.closed_bug_95perc = self.repo_find.closed_bug_95perc
        resp_json.analytic.closed_bug_50perc = self.repo_find.closed_bug_50perc
        resp_json.analytic.upd_major_ver = self.repo_find.upd_major_ver
        resp_json.analytic.upd_minor_ver = self.repo_find.upd_minor_ver
        resp_json.analytic.upd_patch_ver = self.repo_find.upd_patch_ver
        resp_json.analytic.bug_issues_no_comment = self.repo_find.bug_issues_no_comment
        resp_json.analytic.bug_issues_closed_2months = self.repo_find.bug_issues_closed_2months
        resp_json.analytic.pr_closed_count = self.repo_find.pr_closed_count
        resp_json.analytic.pr_closed_duration = self.repo_find.pr_closed_duration
        resp_json.query_info.code = 200
        resp_json.query_info.cost = 0
        resp_json.query_info.database = f'Information from the database for {str(self.repo_find.upd_date)} UTC'

    def find_repository(self):
        self.repo_find = models.RepositoryInfo.query.filter(
            func.lower(models.RepositoryInfo.repo_path) == self.repository_path.lower(),
        ).first()
