import backend.analytic.use_graphql as ug
import backend.analytic.functions as fn
import backend.analytic.bug_issues as bi
from datetime import datetime, timedelta
from loguru import logger
import asyncio


class GithubApiClient:
    """
    Данный класс собирает данные из GitHub, проводит аналитику, формирует resp_json.
    get_info_labels - получение общей информации о репозитории и информации о labels
        Внутри себя использует:
        get_info_labels_json - для получения данных от GitHub
        parse_info_labels - для обработки полученных данных
            parsing_version - для аналитики версионирований репозитория
            pull_request_analytics - для аналитики PR
    Если общей информации достаточно, возвращает resp_json.
    Если нужна аналитика по bug_issues, то продолжает собирать данные.
    get_bug_issues - сбор информации по bug_issues
        Внутри себя использует:
        get_info_labels_json - для получения данных от GitHub
        parse_bug_issues - для обработки полученных данных
            push_bug_issues - для сбора данных о bug_issues
    get_bug_analytic - получение аналитики по собранной bug_issues информации

    :param rec_request: ReceivedRequest (DTO), запрос полученный от пользователя
    :param resp_json: RequestResponse (DTO), для подготовки ответа на запрос
    :return: resp_json: RequestResponse (DTO), ответ на запрос
    """

    async def get_new_report(self, rec_request, resp_json):
        self.rec_request = rec_request
        self.resp_json = resp_json
        self.resp_json.meta.request_downtime = timedelta(seconds=0)
        await self.get_info_labels()  # Получает общую информации о репозитории и информации о labels
        if resp_json.meta.code:  # Если resp_json содержит код (была ошибка), то возвращаем resp_json
            return self.resp_json
        if self.rec_request.response_type == 'repo':  # Если информации о репозитории достаточно...
            self.resp_json.meta.code = 200
            logger.info(f'GH_200/repo, rec_request={self.rec_request.dict(exclude={"token"})}, {self.resp_json=}')
            return self.resp_json  # ... то возвращаем успешный resp_json с этими данными
        await self.get_bug_issues()  # Сбор информации по bug_issues
        if resp_json.meta.code:  # Если resp_json содержит код (была ошибка), то возвращаем resp_json
            return self.resp_json
        self.resp_json = await self.instance_b_i_a.get_bug_analytic(self.resp_json)  # Проводим аналитику данных
        self.resp_json.meta.code = 200
        logger.info(f'GH_200, rec_request={self.rec_request.dict(exclude={"token"})}, {self.resp_json=}')
        return self.resp_json  # Возвращаем успешный resp_json

    async def get_info_labels(self):
        self.cursor = None
        self.repo_labels_name_list = []
        self.data_github = ug.UseGraphQL()
        error_count = 0

        while True:
            self.resp_json, self.data = await self.data_github.get_info_labels_json(  # Обращаемся к GitHub
                rec_request=self.rec_request,
                resp_json=self.resp_json,
                cursor=self.cursor,
            )
            if self.resp_json.meta.code:  # Если resp_json содержит код (была ошибка), то возвращаем resp_json
                return self.resp_json
            if self.data.get('data'):
                await self.parse_info_labels()  # Если есть полученные данные, то начинаем обработку
                if self.resp_json.meta.code:
                    return self.resp_json
            else:
                if error_count < 11:
                    logger.error(
                        f'GET_DATA_ERROR! {self.data=}, rec_request={self.rec_request.dict(exclude={"token"})}, '
                        f'{self.resp_json=}')
                    error_count += 1
                    await asyncio.sleep(1)  # Если полученных данные нет, то повторяем запрос через 1 секунду
                    continue
                else:
                    return await fn.internal_error_500(
                        rec_request=self.rec_request,
                        resp_json=self.resp_json,
                        e_data=self.data,
                    )

            if self.has_next_page:  # Если есть еще страницы (labels > 100), повторяем считывание
                self.cursor = self.end_cursor
            else:
                break  # Если страниц нет, выходим из цикла

        # Проверяем labels на содержание 'bug' в названии, bug_labels используем для поиска bug_issues
        self.repo_labels_bug_list = []
        for name in self.repo_labels_name_list:
            if 'bug' in name.lower():
                self.repo_labels_bug_list.append(name)

    async def parse_info_labels(self):
        try:
            if not self.cursor:  # Если идет обработка первого запроса (cursor == None)
                self.resp_json.data.owner = self.data['data']['repository']['owner']['login']
                self.resp_json.data.name = self.data['data']['repository']['name']
                self.resp_json.data.description = self.data['data']['repository']['description']
                self.resp_json.data.stars = self.data['data']['repository']['stargazerCount']
                self.resp_json.data.created_at = await fn.to_date(self.data['data']['repository']['createdAt'])
                self.resp_json.data.duration = (
                        datetime.utcnow() - self.resp_json.data.created_at
                ).days
                self.resp_json.data.updated_at = (
                        datetime.utcnow() - await fn.to_date(self.data['data']['repository']['updatedAt'])
                ).days
                self.resp_json.data.pushed_at = (
                        datetime.utcnow() - await fn.to_date(self.data['data']['repository']['pushedAt'])
                ).days
                self.resp_json.data.archived = self.data['data']['repository']['isArchived']
                self.resp_json.data.locked = self.data['data']['repository']['isLocked']
                self.resp_json.data.watchers_count = self.data['data']['repository']['watchers']['totalCount']
                self.resp_json.data.fork_count = self.data['data']['repository']['forkCount']
                self.resp_json.data.issues_count = self.data['data']['repository']['issues']['totalCount']
                if self.data['data']['repository']['releases']['edges']:
                    self.resp_json.data.version = \
                        self.data['data']['repository']['releases']['edges'][0]['node']['tag']['name']
                    self.resp_json = await fn.parsing_version(
                        resp_json=self.resp_json,
                        data=self.data['data']['repository']['releases']['edges'],
                    )
                if self.data['data']['repository']['pullRequests']['nodes']:
                    self.resp_json = await fn.pull_request_analytics(
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
        except KeyError as e:  # Обработка ошибки при некорректном ответе data от GitHub
            return await fn.internal_error_500(
                rec_request=self.rec_request,
                resp_json=self.resp_json,
                e_data=self.data,
                error=e,
            )
        except TypeError as e:  # Обработка ошибки если репозиторий не найден на GitHub
            return await fn.json_error_404(
                rec_request=self.rec_request,
                resp_json=self.resp_json,
                error=self.data['errors'][0]['message'],
                e=e,
            )

    async def get_bug_issues(self):
        self.cursor = None
        self.instance_b_i_a = bi.BugIssuesAnalytic()
        error_count = 0

        while True:
            self.resp_json, self.data = await self.data_github.get_bug_issues_json(  # Обращаемся к GitHub
                rec_request=self.rec_request,
                resp_json=self.resp_json,
                cursor=self.cursor,
                repo_labels_bug_list=self.repo_labels_bug_list,
            )
            if self.resp_json.meta.code:  # Если resp_json содержит код (была ошибка), то возвращаем resp_json
                return self.resp_json
            if self.data.get('data'):
                await self.parse_bug_issues()  # Если есть полученные данные, то начинаем обработку
            else:
                if error_count < 11:
                    logger.error(f'GET_DATA_ERROR! {self.data=}, rec_request={self.rec_request.dict(exclude={"token"})}, '
                                 f'{self.resp_json=}')
                    error_count += 1
                    await asyncio.sleep(1)  # Если полученных данные нет, то повторяем запрос через 1 секунду
                    continue
                else:
                    return await fn.internal_error_500(
                        rec_request=self.rec_request,
                        resp_json=self.resp_json,
                        e_data=self.data,
                    )

            # Если идет обработка первого запроса (cursor == None) и если количество bug_issues > 200
            if not self.cursor and self.resp_json.data.bug_issues_count > 200:

                # Предварительный расчет времени запроса
                cost_multiplier = 2.9  # Множитель запроса (100 bug_issues в секундах)
                cost_upped = cost_multiplier * 2  # Дополнительная погрешность
                self.resp_json.meta.estimated_time = str(round(
                    ((self.resp_json.data.bug_issues_count // 100) * cost_multiplier) + cost_upped, 2)
                )
                # Запускаем дополнительную корутину для выода предпологаемого времени на форму сайта
                asyncio.run_coroutine_threadsafe(
                    self.output_estimated_time(estimated_time=self.resp_json.meta.estimated_time),
                    asyncio.get_running_loop()
                )

            if self.has_next_page:  # Если есть еще страницы (считаны не все bug_issues), повторяем считывание
                self.cursor = self.end_cursor
            else:
                break  # Если страниц нет, выходим из цикла

    async def parse_bug_issues(self):
        try:
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
        except Exception as e:  # Логирование ошибки, чтоб знать что обрабатывать
            logger.error(f'ERROR! {self.data=}, {e=}, rec_request={self.rec_request.dict(exclude={"token"})}, '
                         f'{self.resp_json=}')

    async def output_estimated_time(self, estimated_time):
        # Планируется вывод на форму сайта
        logger.info(f'{estimated_time=}, rec_request={self.rec_request.dict(exclude={"token"})}')
