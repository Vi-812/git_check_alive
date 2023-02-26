import os
from backend import github_api_client as ga
from backend import func_api_client as fa
from frontend import models, db, load_dotenv
from datetime import datetime
from hashlib import blake2s
from dto.req_response import RequestResponse


class DataBaseHandler:
    async def get_report(self, repository_path, token, force=True, response_type='full'):
        self.response_duration_time = datetime.utcnow()
        self.resp_json = RequestResponse(repository_info={}, analytic={}, query_info={})
        self.token = token
        self.response_type = response_type
        try:
            repository_path = repository_path.split('/')
            repository_path = repository_path[-2] + '/' + repository_path[-1]
        except IndexError as e:
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
        final_block_r = await self.final_block()

        if self.resp_json.query_info.code == 200:
            await self.save_or_upd_repo_data()
            await self.collection_repo()
            # Валидация стоимости запроса, записывать ли в статистику
            if self.resp_json.query_info.cost > 10:
                await self.save_statistics()
        return final_block_r

    async def save_or_upd_repo_data(self):
        self.repository_path = self.resp_json.repository_info.owner + '/' + self.resp_json.repository_info.name
        await self.find_repository('RepositoryInfo')
        if self.repo_find:
            await self.update_repo_data()
        else:
            await self.create_repo_data()

    async def create_repo_data(self):
        repo_data = models.RepositoryInfo(
            repo_path=self.resp_json.repository_info.owner + '/' + self.resp_json.repository_info.name,
            description=self.resp_json.repository_info.description,
            stars=self.resp_json.repository_info.stars,
            version=self.resp_json.repository_info.version,
            created_at=self.resp_json.repository_info.created_at,
            duration=self.resp_json.repository_info.duration,
            updated_at=self.resp_json.repository_info.updated_at,
            pushed_at=self.resp_json.repository_info.pushed_at,
            archived=self.resp_json.repository_info.archived,
            locked=self.resp_json.repository_info.locked,
            issues_count=self.resp_json.repository_info.issues_count,
            bug_issues_count=self.resp_json.repository_info.bug_issues_count,
            bug_issues_closed_count=self.resp_json.repository_info.bug_issues_closed_count,
            bug_issues_open_count=self.resp_json.repository_info.bug_issues_open_count,
            watchers_count=self.resp_json.repository_info.watchers_count,
            fork_count=self.resp_json.repository_info.fork_count,
            closed_bug_95perc=self.resp_json.analytic.closed_bug_95perc,
            closed_bug_50perc=self.resp_json.analytic.closed_bug_50perc,
            upd_major_ver=self.resp_json.analytic.upd_major_ver,
            upd_minor_ver=self.resp_json.analytic.upd_minor_ver,
            upd_patch_ver=self.resp_json.analytic.upd_patch_ver,
            bug_issues_no_comment=self.resp_json.analytic.bug_issues_no_comment,
            bug_issues_closed_2months=self.resp_json.analytic.bug_issues_closed_2months,
            pr_closed_count=self.resp_json.analytic.pr_closed_count,
            pr_closed_duration=self.resp_json.analytic.pr_closed_duration,
            time=self.resp_json.query_info.time,
            cost=self.resp_json.query_info.cost,
        )
        db.session.add(repo_data)
        db.session.commit()

    async def update_repo_data(self):
        self.repo_find.description = self.resp_json.repository_info.description
        self.repo_find.stars = self.resp_json.repository_info.stars
        self.repo_find.version = self.resp_json.repository_info.version
        self.repo_find.created_at = self.resp_json.repository_info.created_at
        self.repo_find.duration = self.resp_json.repository_info.duration
        self.repo_find.updated_at = self.resp_json.repository_info.updated_at
        self.repo_find.pushed_at = self.resp_json.repository_info.pushed_at
        self.repo_find.archived = self.resp_json.repository_info.archived
        self.repo_find.locked = self.resp_json.repository_info.locked
        self.repo_find.issues_count = self.resp_json.repository_info.issues_count
        self.repo_find.bug_issues_count = self.resp_json.repository_info.bug_issues_count
        self.repo_find.bug_issues_closed_count = self.resp_json.repository_info.bug_issues_closed_count
        self.repo_find.bug_issues_open_count = self.resp_json.repository_info.bug_issues_open_count
        self.repo_find.watchers_count = self.resp_json.repository_info.watchers_count
        self.repo_find.fork_count = self.resp_json.repository_info.fork_count
        self.repo_find.closed_bug_95perc = self.resp_json.analytic.closed_bug_95perc
        self.repo_find.closed_bug_50perc = self.resp_json.analytic.closed_bug_50perc
        self.repo_find.upd_major_ver = self.resp_json.analytic.upd_major_ver
        self.repo_find.upd_minor_ver = self.resp_json.analytic.upd_minor_ver
        self.repo_find.upd_patch_ver = self.resp_json.analytic.upd_patch_ver
        self.repo_find.bug_issues_no_comment = self.resp_json.analytic.bug_issues_no_comment
        self.repo_find.bug_issues_closed_2months = self.resp_json.analytic.bug_issues_closed_2months
        self.repo_find.pr_closed_count = self.resp_json.analytic.pr_closed_count
        self.repo_find.pr_closed_duration = self.resp_json.analytic.pr_closed_duration
        self.repo_find.time = self.resp_json.query_info.time
        self.repo_find.cost = self.resp_json.query_info.cost
        db.session.commit()

    async def load_repo_data(self):
        self.resp_json.repository_info.owner, self.resp_json.repository_info.name = self.repo_find.repo_path.split('/', 2)
        self.resp_json.repository_info.description = self.repo_find.description
        self.resp_json.repository_info.stars = self.repo_find.stars
        self.resp_json.repository_info.version = self.repo_find.version
        self.resp_json.repository_info.created_at = self.repo_find.created_at
        self.resp_json.repository_info.duration = self.repo_find.duration
        self.resp_json.repository_info.updated_at = self.repo_find.updated_at
        self.resp_json.repository_info.pushed_at = self.repo_find.pushed_at
        self.resp_json.repository_info.archived = self.repo_find.archived
        self.resp_json.repository_info.locked = self.repo_find.locked
        self.resp_json.repository_info.issues_count = self.repo_find.issues_count
        self.resp_json.repository_info.bug_issues_count = self.repo_find.bug_issues_count
        self.resp_json.repository_info.bug_issues_closed_count = self.repo_find.bug_issues_closed_count
        self.resp_json.repository_info.bug_issues_open_count = self.repo_find.bug_issues_open_count
        self.resp_json.repository_info.watchers_count = self.repo_find.watchers_count
        self.resp_json.repository_info.fork_count = self.repo_find.fork_count
        self.resp_json.analytic.closed_bug_95perc = self.repo_find.closed_bug_95perc
        self.resp_json.analytic.closed_bug_50perc = self.repo_find.closed_bug_50perc
        self.resp_json.analytic.upd_major_ver = self.repo_find.upd_major_ver
        self.resp_json.analytic.upd_minor_ver = self.repo_find.upd_minor_ver
        self.resp_json.analytic.upd_patch_ver = self.repo_find.upd_patch_ver
        self.resp_json.analytic.bug_issues_no_comment = self.repo_find.bug_issues_no_comment
        self.resp_json.analytic.bug_issues_closed_2months = self.repo_find.bug_issues_closed_2months
        self.resp_json.analytic.pr_closed_count = self.repo_find.pr_closed_count
        self.resp_json.analytic.pr_closed_duration = self.repo_find.pr_closed_duration
        self.resp_json.query_info.code = 200
        self.resp_json.query_info.cost = 0
        self.resp_json.query_info.database = f'Information from the database for {str(self.repo_find.upd_date)} UTC'

    async def save_statistics(self):
        time = self.resp_json.query_info.time
        cost = self.resp_json.query_info.cost
        if self.resp_json.query_info.remains < 3000:
            query_limit = self.resp_json.query_info.remains
        else:
            query_limit = None
        statistic = models.QueryStatistics(
            repo_path=self.resp_json.repository_info.owner + '/' + self.resp_json.repository_info.name,
            issues_count=self.resp_json.repository_info.issues_count,
            bug_issues_count=self.resp_json.repository_info.bug_issues_count,
            time=time,
            cost=cost,
            request_kf=round(time/cost, 3),
            query_limit=query_limit,
            rt=self.resp_json.query_info.rt
        )
        db.session.add(statistic)
        db.session.commit()

    async def collection_repo(self):
        await self.find_repository('RepositoryCollection')
        if not self.repo_find:
            load_dotenv()
            hasher = os.getenv('HASHER')
            token_hash = blake2s(digest_size=32)
            token_hash.update((hasher + self.token + hasher).encode('utf-8'))
            token_hash = (token_hash.digest()).decode('ascii', errors='ignore')

            new_repo = models.RepositoryCollection(
                repo_path=self.resp_json.repository_info.owner + '/' + self.resp_json.repository_info.name,
                token_hash=str(token_hash),
            )
            db.session.add(new_repo)
            db.session.commit()

    async def find_repository(self, table):


        self.repo_find = eval(f'models.{table}.query.filter(func.lower(models.{table}.repo_path) == self.repository_path.lower(),).first()')

    async def final_block(self):
        code = self.resp_json.query_info.code
        if code != 200:
            self.resp_json.__delattr__('repository_info')
            self.resp_json.__delattr__('analytic')
        self.response_duration_time = datetime.utcnow() - self.response_duration_time
        self.resp_json.query_info.time = round(
            self.response_duration_time.seconds + (self.response_duration_time.microseconds * 0.000001), 2
        )
        self.resp_json.query_info.ght = round(
            self.resp_json.query_info.ght.seconds + (self.resp_json.query_info.ght.microseconds * 0.000001), 2
        )
        if self.resp_json.query_info.rt:
            self.resp_json.query_info.rt += '/' + str(self.resp_json.query_info.time)
        return self.resp_json.json(by_alias=True), code
