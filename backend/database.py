import os
from datetime import datetime
from hashlib import blake2s
from backend import github_api_client as ga
from backend import func_api_client as fa
from frontend import load_dotenv, db, models
from dto.req_response import RequestResponse
from sqlalchemy import func
from sqlalchemy.orm import Session


class DataBaseHandler:
    async def get_report(self, repository_path, token, force=False, response_type='full'):
        self.response_duration_time = datetime.utcnow()
        self.resp_json = RequestResponse(data={}, analytic={}, meta={})
        self.token = token
        self.response_type = response_type
        try:
            repository_path = repository_path.split('/')
            repository_path = repository_path[-2] + '/' + repository_path[-1]
        except (IndexError, AttributeError) as e:
            await fa.path_error_400(
                resp_json=self.resp_json,
                repository_path=repository_path,
                e=e,
            )
            return await self.final_block()
        self.repository_path = repository_path
        await self.find_repository('RepositoryInfo')
        # Проверка что репозиторий найден в БД и forse=False
        if self.repo_find and not force:
            # Проверка актуальности репозитория, данные в БД обновляются если с момента запроса прошло N часов
            # Количество прошедших часов (hours) должно ровняться или привышать стоимость запроса (request_cost)
            # Если времени прошло не достаточно, данные загружаются из БД
            hours = ((datetime.utcnow() - self.repo_find.upd_date)*24).days
            if hours < self.repo_find.cost:
                await self.load_repo_data()
                return await self.final_block()

        instance_api_client = ga.GithubApiClient(token=self.token)
        self.resp_json = await instance_api_client.get_new_report(
            resp_json=self.resp_json,
            repository_path=self.repository_path,
            response_type=self.response_type,
        )

        await self.time_block()
        if self.resp_json.meta.code == 200:
            await self.create_or_update_repo_data()
            await self.save_collection()
            # Валидация стоимости запроса, записывать ли в статистику
            if self.resp_json.meta.cost > 10:
                await self.save_statistics()
        return await self.final_block(t_block=False)

    async def create_or_update_repo_data(self):
        self.repository_path = self.resp_json.data.owner + '/' + self.resp_json.data.name
        await self.find_repository('RepositoryInfo')
        if self.repo_find:
            await self.update_repo_data()
        else:
            await self.create_repo_data()

    async def create_repo_data(self):
        session = Session(bind=db)
        repo_data = models.RepositoryInfo(
            repo_path=self.resp_json.data.owner + '/' + self.resp_json.data.name,
            description=self.resp_json.data.description,
            stars=self.resp_json.data.stars,
            version=self.resp_json.data.version,
            created_at=self.resp_json.data.created_at,
            duration=self.resp_json.data.duration,
            updated_at=self.resp_json.data.updated_at,
            pushed_at=self.resp_json.data.pushed_at,
            archived=self.resp_json.data.archived,
            locked=self.resp_json.data.locked,
            issues_count=self.resp_json.data.issues_count,
            bug_issues_count=self.resp_json.data.bug_issues_count,
            bug_issues_closed_count=self.resp_json.data.bug_issues_closed_count,
            bug_issues_open_count=self.resp_json.data.bug_issues_open_count,
            watchers_count=self.resp_json.data.watchers_count,
            fork_count=self.resp_json.data.fork_count,
            closed_bug_95perc=self.resp_json.analytic.closed_bug_95perc,
            closed_bug_50perc=self.resp_json.analytic.closed_bug_50perc,
            upd_major_ver=self.resp_json.analytic.upd_major_ver,
            upd_minor_ver=self.resp_json.analytic.upd_minor_ver,
            upd_patch_ver=self.resp_json.analytic.upd_patch_ver,
            bug_issues_no_comment=self.resp_json.analytic.bug_issues_no_comment,
            bug_issues_closed_2months=self.resp_json.analytic.bug_issues_closed_2months,
            pr_closed_count=self.resp_json.analytic.pr_closed_count,
            pr_closed_duration=self.resp_json.analytic.pr_closed_duration,
            time=self.resp_json.meta.time,
            cost=self.resp_json.meta.cost,
        )
        session.add(repo_data)
        session.commit()

    async def update_repo_data(self):
        session = Session(bind=db)
        self.repo_find.description = self.resp_json.data.description
        self.repo_find.stars = self.resp_json.data.stars
        self.repo_find.version = self.resp_json.data.version
        self.repo_find.created_at = self.resp_json.data.created_at
        self.repo_find.duration = self.resp_json.data.duration
        self.repo_find.updated_at = self.resp_json.data.updated_at
        self.repo_find.pushed_at = self.resp_json.data.pushed_at
        self.repo_find.archived = self.resp_json.data.archived
        self.repo_find.locked = self.resp_json.data.locked
        self.repo_find.issues_count = self.resp_json.data.issues_count
        self.repo_find.bug_issues_count = self.resp_json.data.bug_issues_count
        self.repo_find.bug_issues_closed_count = self.resp_json.data.bug_issues_closed_count
        self.repo_find.bug_issues_open_count = self.resp_json.data.bug_issues_open_count
        self.repo_find.watchers_count = self.resp_json.data.watchers_count
        self.repo_find.fork_count = self.resp_json.data.fork_count
        self.repo_find.closed_bug_95perc = self.resp_json.analytic.closed_bug_95perc
        self.repo_find.closed_bug_50perc = self.resp_json.analytic.closed_bug_50perc
        self.repo_find.upd_major_ver = self.resp_json.analytic.upd_major_ver
        self.repo_find.upd_minor_ver = self.resp_json.analytic.upd_minor_ver
        self.repo_find.upd_patch_ver = self.resp_json.analytic.upd_patch_ver
        self.repo_find.bug_issues_no_comment = self.resp_json.analytic.bug_issues_no_comment
        self.repo_find.bug_issues_closed_2months = self.resp_json.analytic.bug_issues_closed_2months
        self.repo_find.pr_closed_count = self.resp_json.analytic.pr_closed_count
        self.repo_find.pr_closed_duration = self.resp_json.analytic.pr_closed_duration
        self.repo_find.time = self.resp_json.meta.time
        self.repo_find.cost = self.resp_json.meta.cost
        session.add(self.repo_find)
        session.commit()

    async def load_repo_data(self):
        self.resp_json.data.owner, self.resp_json.data.name = self.repo_find.repo_path.split('/', 2)
        self.resp_json.data.description = self.repo_find.description
        self.resp_json.data.stars = self.repo_find.stars
        self.resp_json.data.version = self.repo_find.version
        self.resp_json.data.created_at = self.repo_find.created_at
        self.resp_json.data.duration = self.repo_find.duration
        self.resp_json.data.updated_at = self.repo_find.updated_at
        self.resp_json.data.pushed_at = self.repo_find.pushed_at
        self.resp_json.data.archived = self.repo_find.archived
        self.resp_json.data.locked = self.repo_find.locked
        self.resp_json.data.issues_count = self.repo_find.issues_count
        self.resp_json.data.bug_issues_count = self.repo_find.bug_issues_count
        self.resp_json.data.bug_issues_closed_count = self.repo_find.bug_issues_closed_count
        self.resp_json.data.bug_issues_open_count = self.repo_find.bug_issues_open_count
        self.resp_json.data.watchers_count = self.repo_find.watchers_count
        self.resp_json.data.fork_count = self.repo_find.fork_count
        self.resp_json.analytic.closed_bug_95perc = self.repo_find.closed_bug_95perc
        self.resp_json.analytic.closed_bug_50perc = self.repo_find.closed_bug_50perc
        self.resp_json.analytic.upd_major_ver = self.repo_find.upd_major_ver
        self.resp_json.analytic.upd_minor_ver = self.repo_find.upd_minor_ver
        self.resp_json.analytic.upd_patch_ver = self.repo_find.upd_patch_ver
        self.resp_json.analytic.bug_issues_no_comment = self.repo_find.bug_issues_no_comment
        self.resp_json.analytic.bug_issues_closed_2months = self.repo_find.bug_issues_closed_2months
        self.resp_json.analytic.pr_closed_count = self.repo_find.pr_closed_count
        self.resp_json.analytic.pr_closed_duration = self.repo_find.pr_closed_duration
        self.resp_json.meta.code = 200
        self.resp_json.meta.cost = 0
        self.resp_json.meta.database = f'Information from DB at {str(self.repo_find.upd_date)} UTC'

    async def save_statistics(self):
        session = Session(bind=db)
        time = self.resp_json.meta.time
        cost = self.resp_json.meta.cost
        if self.resp_json.meta.remains < 3000:
            query_limit = self.resp_json.meta.remains
        else:
            query_limit = None
        statistic = models.QueryStatistics(
            repo_path=self.resp_json.data.owner + '/' + self.resp_json.data.name,
            issues_count=self.resp_json.data.issues_count,
            bug_issues_count=self.resp_json.data.bug_issues_count,
            time=time,
            cost=cost,
            request_kf=round(time/cost, 3),
            query_limit=query_limit,
            estimated_time=self.resp_json.meta.estimated_time,
            request_downtime=self.resp_json.meta.request_downtime,
        )
        session.add(statistic)
        session.commit()

    async def save_collection(self):
        await self.find_repository('RepositoryCollection')
        if not self.repo_find:
            session = Session(bind=db)
            load_dotenv()
            hasher = os.getenv('HASHER')
            token_hash = blake2s(digest_size=32)
            token_hash.update((hasher + self.token + hasher).encode('utf-8'))
            token_hash = (token_hash.digest()).decode('ascii', errors='ignore')

            new_repo = models.RepositoryCollection(
                repo_path=self.resp_json.data.owner + '/' + self.resp_json.data.name,
                token_hash=str(token_hash),
            )
            session.add(new_repo)
            session.commit()

    async def find_repository(self, table):
        session = Session(bind=db)
        self.repo_find = eval(f'session.query(models.{table}).filter(func.lower(models.{table}.repo_path) == self.repository_path.lower()).first()')
        session.close()


    async def time_block(self):
        self.response_duration_time = datetime.utcnow() - self.response_duration_time
        self.resp_json.meta.time = round(
            self.response_duration_time.seconds + (self.response_duration_time.microseconds * 0.000001), 2
        )
        if self.resp_json.meta.request_downtime:
            self.resp_json.meta.request_downtime = round(
                self.resp_json.meta.request_downtime.seconds + (
                            self.resp_json.meta.request_downtime.microseconds * 0.000001), 2
            )

    async def final_block(self, t_block=True):
        if t_block:
            await self.time_block()
        code = self.resp_json.meta.code
        if code == 200:
            pass
        else:
            self.resp_json.__delattr__('data')
            self.resp_json.__delattr__('analytic')
        return self.resp_json.json(by_alias=True), code
