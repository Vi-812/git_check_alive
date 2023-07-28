import os
from datetime import datetime
from hashlib import blake2s
from app.backend.analytic import github_api_client as ga
from app.backend.analytic import errors_handler as eh
from app.frontend import models
from app.core.settings import load_dotenv, db
from sqlalchemy.orm import Session
from sqlalchemy import func  # Используется
from app.backend.json_preparation import final_json_preparation
from loguru import logger


class DataBaseHandler:
    """
    Данный класс получает запрос от web сервера,проверяет есть ли данный репозиторий в базе и подходят ли условия для
    загрузки. Если условия удовлетворяют, загружает resp_json из базы данных. В ином случае перенаправляет запрос
    в GithubApiClient.
    Так же занимается записью полученных ответов и статистики в базу данных.
    """

    async def get_report(self, rec_request, resp_json):
        self.response_duration_time = datetime.utcnow()  # Засекаем время выполнения запроса
        self.rec_request = rec_request
        self.resp_json = resp_json
        repository_path = self.rec_request.repo_path
        try:
            repository_path = repository_path.split('/')  # Распознаем repository_path
            self.rec_request.repo_owner, self.rec_request.repo_name = repository_path[-2], repository_path[-1]
            self.rec_request.repo_path = self.rec_request.repo_owner + '/' + self.rec_request.repo_name
        except (IndexError, AttributeError) as e:  # Обработка ошибки при неверной передаче repository_path
            self.resp_json = await eh.path_error_400(
                rec_request=self.rec_request,
                resp_json=self.resp_json,
                repository_path=repository_path,
                e=e,
            )
            return await final_json_preparation(rec_request=self.rec_request, resp_json=self.resp_json)


        # Проверка, что skip_cache=False (допускается отчет из БД)
        if not self.rec_request.skip_cache:
            await self.find_repository(table='RepositoryInfo', path=self.rec_request.repo_path)  # Ищем репозиторий
            if self.repo_find:
                # Проверка актуальности репозитория, данные в БД обновляются если с момента запроса прошло N часов
                # Количество прошедших часов (hours) должно ровняться или превышать стоимость запроса (cost)
                # Если времени прошло не достаточно, данные актуальны, ответ загружаем из БД
                hours = ((datetime.utcnow() - self.repo_find.upd_date)*24).days
                if hours < self.repo_find.cost:
                    await self.load_repo_data()  # Загружаем resp_json из БД
                    logger.info(f'DB_200, rec_request={rec_request.dict(exclude={"token"})}, {self.resp_json=}')
                    return await final_json_preparation(rec_request=self.rec_request, resp_json=self.resp_json)

        instance_api_client = ga.GithubApiClient()  # Запрашиваем аналитику у GithubApiClient
        self.resp_json = await instance_api_client.get_new_report(
            rec_request=self.rec_request,
            resp_json=self.resp_json,
        )

        await self.time_block()  # Закрываем time поля
        if self.resp_json.meta.code == 200: # Если запрос с кодом 200, записываем в RepositoryCollection
            self.repository_path = self.resp_json.data.owner + '/' + self.resp_json.data.name
            await self.save_collection()
            if self.rec_request.response_type != 'repo':  # Если запрос не 'repo', записываем в RepositoryInfo
                await self.create_or_update_repo_data()  # Создание или обновление данных
                if self.resp_json.meta.cost > 10:  # Если стоимость > 10, записываем в QueryStatistics
                    await self.save_statistics()
        return await final_json_preparation(rec_request=self.rec_request, resp_json=self.resp_json)

    async def create_or_update_repo_data(self):
        await self.find_repository(table='RepositoryInfo', path=self.repository_path)  # Ищем репозиторий
        if self.repo_find:
            await self.update_repo_data()  # Найден - обновляем
        else:
            await self.create_repo_data()  # Не найден - создаем новый

    async def create_repo_data(self):  # Создаем новый репозиторий в RepositoryInfo
        session = Session(bind=db)
        repo_data = models.RepositoryInfo(
            repo_path=self.resp_json.data.owner + '/' + self.resp_json.data.name,
            description=self.resp_json.data.description,
            stars=self.resp_json.data.stars,
            version=self.resp_json.data.version,
            created_at=self.resp_json.data.created_at,
            existence_time=self.resp_json.data.existence_time,
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
            closed_bug_95perc=self.resp_json.data.closed_bug_95perc,
            closed_bug_50perc=self.resp_json.data.closed_bug_50perc,
            upd_major_ver=self.resp_json.data.upd_major_ver,
            upd_minor_ver=self.resp_json.data.upd_minor_ver,
            upd_patch_ver=self.resp_json.data.upd_patch_ver,
            bug_issues_no_comment=self.resp_json.data.bug_issues_no_comment,
            bug_issues_closed2m=self.resp_json.data.bug_issues_closed2m,
            pr_closed_count2m=self.resp_json.data.pr_closed_count2m,
            pr_closed_duration=self.resp_json.data.pr_closed_duration,
            time=self.resp_json.meta.time,
            cost=self.resp_json.meta.cost,
        )
        session.add(repo_data)
        session.commit()

    async def update_repo_data(self):  # Обновляем существующий репозиторий в RepositoryInfo
        session = Session(bind=db)
        self.repo_find.description = self.resp_json.data.description
        self.repo_find.stars = self.resp_json.data.stars
        self.repo_find.version = self.resp_json.data.version
        self.repo_find.created_at = self.resp_json.data.created_at
        self.repo_find.existence_time = self.resp_json.data.existence_time
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
        self.repo_find.closed_bug_95perc = self.resp_json.data.closed_bug_95perc
        self.repo_find.closed_bug_50perc = self.resp_json.data.closed_bug_50perc
        self.repo_find.upd_major_ver = self.resp_json.data.upd_major_ver
        self.repo_find.upd_minor_ver = self.resp_json.data.upd_minor_ver
        self.repo_find.upd_patch_ver = self.resp_json.data.upd_patch_ver
        self.repo_find.bug_issues_no_comment = self.resp_json.data.bug_issues_no_comment
        self.repo_find.bug_issues_closed2m = self.resp_json.data.bug_issues_closed2m
        self.repo_find.pr_closed_count2m = self.resp_json.data.pr_closed_count2m
        self.repo_find.pr_closed_duration = self.resp_json.data.pr_closed_duration
        self.repo_find.time = self.resp_json.meta.time
        self.repo_find.cost = self.resp_json.meta.cost
        session.add(self.repo_find)
        session.commit()

    async def load_repo_data(self):  # Загружаем resp_json из БД (RepositoryInfo)
        self.resp_json.data.owner, self.resp_json.data.name = self.repo_find.repo_path.split('/', 2)
        self.resp_json.data.description = self.repo_find.description
        self.resp_json.data.stars = self.repo_find.stars
        self.resp_json.data.version = self.repo_find.version
        self.resp_json.data.created_at = self.repo_find.created_at
        self.resp_json.data.existence_time = self.repo_find.existence_time
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
        self.resp_json.data.closed_bug_95perc = self.repo_find.closed_bug_95perc
        self.resp_json.data.closed_bug_50perc = self.repo_find.closed_bug_50perc
        self.resp_json.data.upd_major_ver = self.repo_find.upd_major_ver
        self.resp_json.data.upd_minor_ver = self.repo_find.upd_minor_ver
        self.resp_json.data.upd_patch_ver = self.repo_find.upd_patch_ver
        self.resp_json.data.bug_issues_no_comment = self.repo_find.bug_issues_no_comment
        self.resp_json.data.bug_issues_closed2m = self.repo_find.bug_issues_closed2m
        self.resp_json.data.pr_closed_count2m = self.repo_find.pr_closed_count2m
        self.resp_json.data.pr_closed_duration = self.repo_find.pr_closed_duration
        self.resp_json.meta.code = 200
        self.resp_json.meta.cost = 0
        self.resp_json.meta.information = f'Data from DB at {str(self.repo_find.upd_date)} UTC'

    async def save_statistics(self):  # Записываем в QueryStatistics
        session = Session(bind=db)
        time = self.resp_json.meta.time
        cost = self.resp_json.meta.cost
        if self.resp_json.meta.remains < 3000:  # Если кредитов осталось меньше 3000, записываем в БД
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

    async def save_collection(self):  # Записываем в RepositoryCollection
        await self.find_repository(table='RepositoryCollection', path=self.repository_path)  # Ищем репозиторий
        if not self.repo_find:  # Если такого репозитория еще нет, записываем
            session = Session(bind=db)
            load_dotenv()
            hasher = os.getenv('HASHER')
            token_hash = blake2s(digest_size=32)  # Записываем hash токена в БД
            token_hash.update((hasher + self.rec_request.token + hasher).encode('utf-8'))
            token_hash = (token_hash.digest()).decode('utf-8', errors='ignore')

            new_repo = models.RepositoryCollection(
                repo_path=self.resp_json.data.owner + '/' + self.resp_json.data.name,
                token_hash=str(token_hash),
            )
            session.add(new_repo)
            session.commit()

    async def find_repository(self, table, path):
        """
        Ищет репозиторий в таблице=table с вледельцем_именем_репозитория=path.
        :param table: Таблица для поиска
        :param path: Путь для поиска
        :return repo_find: Найденный репозиторий (для считывания или обновления), None если репозиторий не найден
        """
        session = Session(bind=db)
        self.repo_find = eval(f'session.query(models.{table}).filter('
                              f'func.lower(models.{table}.repo_path) == "{path}".lower()'
                              f').first()')
        session.close()

    async def time_block(self):  # Закрываем time поля
        self.response_duration_time = datetime.utcnow() - self.response_duration_time  # Фиксируем время
        self.resp_json.meta.time = round(  # Переводим в нужный нам формат, округляем
            self.response_duration_time.seconds + (self.response_duration_time.microseconds * 0.000001), 2
        )
        if self.resp_json.meta.request_downtime:  # Если есть request_downtime, переводим, округляем
            self.resp_json.meta.request_downtime = round(
                self.resp_json.meta.request_downtime.seconds + (
                            self.resp_json.meta.request_downtime.microseconds * 0.000001), 2
            )
