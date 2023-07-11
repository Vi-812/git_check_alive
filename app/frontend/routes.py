from app.core.settings import templates, token_app
from app.frontend import forms
from app.backend import database
from app.backend.analytic import errors_handler as eh
from app.backend.json_preparation import final_json_preparation
from app.core.data_transfer_objects.received_request import ReceivedRequest
from app.core.data_transfer_objects.answer import RequestResponse
from sanic import HTTPResponse
from loguru import logger
import json
from fastapi import APIRouter


router = APIRouter()


@router.get('/')
async def index(request):
    form = forms.RepositoryPathForm(request)
    return templates.render('index.html', request, form=form, data=None)


@router.get('/values')
async def values(request):
    return templates.render('values.html', request, values_description=values_description)


@router.get('/rest-api')
async def rest_api(request):
    return templates.render('api_help.html', request)


@router.get('/contact')
async def contact(request):
    return templates.render('contact.html', request)


@router.post('/')
async def index_resp(request):
    try:
        form = forms.RepositoryPathForm(request)
        repository_path = request.form.get(['link_repository'][0], None)
        cache = request.headers.get('skipCache', False)
        i_test = request.headers.get('test', '')
        rec_request = ReceivedRequest(url=request.url, repo_path=repository_path, token=token_app, cache=cache)
        resp_json = RequestResponse(data={}, error={}, meta={})  # Создаем экземпляр RequestResponse
    except Exception as e:
        return await global_error(error=e)
    try:
        logger.info(f'<<<|{i_test} rec_request={rec_request.dict(exclude={"token"})}')
        if rec_request.repo_path:
            instance_db_client = database.DataBaseHandler()
            resp_json, code = await instance_db_client.get_report(rec_request=rec_request, resp_json=resp_json)
            resp_json = json.loads(resp_json)
        else:
            resp_json = await eh.path_error_400(rec_request=rec_request,
                                                resp_json=resp_json,
                                                repository_path=repository_path
                                                )
            resp_json, code = await final_json_preparation(rec_request=rec_request, resp_json=resp_json)
            resp_json = json.loads(resp_json)
        logger.info(f'|>>>{i_test} {code=}, rec_request={rec_request.dict(exclude={"token"})}, {resp_json=}')
        return templates.render('index.html', request,
                            status=code,
                            form=form,
                            data=resp_json,
                            values_description=values_description
                            )
    except Exception as e:
        return await global_error(error=e, rec_request=rec_request, resp_json=resp_json)


@router.get('/api/repo')
@router.get('/api/issues-statistic')
@router.get('/api/full')
async def get_api_request(request):
    try:
        repository_path = request.args.get('name', None)
        skip_cache = request.args.get('skipCache', False)
        token_api = request.headers.get('token', None)
        i_test = request.headers.get('test', '')
        if not token_api:
            token_api = token_app
        if '/api/repo' in request.url:
            response_type = 'repo'  # Запрос информации только о репозитории
        elif '/api/issues-statistic' in request.url:
            response_type = 'issues'  # Запрос информации только о issues
        else:
            response_type = 'full'  # Полный запрос
        rec_request = ReceivedRequest(url=request.url, repo_path=repository_path, token=token_api,
                                      skip_cache=skip_cache, response_type=response_type)
        resp_json = RequestResponse(data={}, error={}, meta={})  # Создаем экземпляр RequestResponse
    except Exception as e:
        return await global_error(error=e)
    try:
        logger.info(f'<<<|{i_test} rec_request={rec_request.dict(exclude={"token"})}')
        instance_db_client = database.DataBaseHandler()
        resp_json, code = await instance_db_client.get_report(rec_request=rec_request, resp_json=resp_json)
        logger.info(f'|>>>{i_test} {code=}, rec_request={rec_request.dict(exclude={"token"})}, {resp_json=}')
        return HTTPResponse(resp_json, status=code)
    except Exception as e:
        return await global_error(error=e, rec_request=rec_request, resp_json=resp_json)

@router.post('/api/repo')
@router.post('/api/issues-statistic')
@router.post('/api/full')
async def post_api_request(request):
    try:
        print("START post_api_request")
        repository_path = request.json.get('name', None)
        token_api = request.json.get('token', None)
        skip_cache = request.json.get('skipCache', False)
        i_test = request.headers.get('test', '')
        if not token_api:
            token_api = token_app
        if '/api/repo' in request.url:
            response_type = 'repo'  # Запрос информации только о репозитории
        elif '/api/issues-statistic' in request.url:
            response_type='issues'  # Запрос информации только о issues
        else:
            response_type='full'  # Полный запрос
        rec_request = ReceivedRequest(url=request.url, repo_path=repository_path, token=token_api,
                                      skip_cache=skip_cache,response_type=response_type)
        resp_json = RequestResponse(data={}, error={}, meta={})  # Создаем экземпляр RequestResponse
    except Exception as e:
        return await global_error(error=e)
    try:
        logger.info(f'<<<|{i_test} rec_request={rec_request.dict(exclude={"token"})}')
        instance_db_client = database.DataBaseHandler()
        resp_json, code = await instance_db_client.get_report(rec_request=rec_request, resp_json=resp_json)
        logger.info(f'|>>>{i_test} {code=}, rec_request={rec_request.dict(exclude={"token"})}, {resp_json=}')
        return HTTPResponse(resp_json, status=code)
    except Exception as e:
        return await global_error(error=e, rec_request=rec_request, resp_json=resp_json)


async def global_error(error, rec_request=None, resp_json=RequestResponse(data={}, error={}, meta={})):
    # Создаем глобальный обработчик ошибок для всех непредвиденных ситуаций
    if not rec_request:
        logger.critical(f'GLOBAL_ERROR_500! {error=}, {resp_json=}')
    else:
        logger.critical(f'GLOBAL_ERROR_500! {error=}, rec_request={rec_request.dict(exclude={"token"})}, {resp_json=}')
    resp_json.meta.code = 500
    resp_json.error.error_description = 'Internal Server Error'
    resp_json.error.error_message = str(error)
    return resp_json

values_description = {  # Описание значений resp_json
    'data': {
        'owner': 'Имя владельца репозитория (str)',
        'name': 'Имя репозитория (str)',
        'description': 'Описание (str)',
        'stars': 'Количество звезд (int)',
        'createdAt': 'Дата создания (str iso)',
        'existenceTime': 'Как давно существует (int дней)',
        'updatedAt': 'Время с последнего обновления НЕ КОДА (int дней)',
        'pushedAt': 'Время с последнего обновления КОДА, любая ветка (int дней)',
        'version': 'Текущая версия проекта (str)',
        'updMajorVer': 'Время с обновления Мажорной версии (int дней)',
        'updMinorVer': 'Время с обновления Минорной версии (int дней)',
        'updPatchVer': 'Время с обновления Патч версии (int дней)',
        'prClosedCount2m': 'Количество PR закрытых за последние 2 месяца (int)',
        'prClosedDuration': 'Среднее время закрытия PR (float дней)',
        'archived': 'Репозиторий находится в архиве (bool)',
        'locked': 'Репозиторий закрыт (bool)',
        'watchersCount': 'Количество наблюдателей (int)',
        'forkCount': 'Количество форков (int)',
        'issuesCount': 'Общее количество вопросов (int)',
        'bugIssuesCount': 'Общее количество вопросов в которых присутствуют bug метками (int)',
        'bugIssuesClosedCount': 'Количество закрытых bug-вопросов (int)',
        'bugIssuesOpenCount': 'Количество открытых bug-вопросов (int)',
        'bugIssuesNoComment': 'Какой процент bug-вопросов не имеет комментариев (float % max 100.00)',
        'bugIssuesClosed2m': 'Процент bug-вопросов решенных быстрее 2х месяцев, '
                             'от общего числа решенных bug-вопросов (float % max 100.00)',
        'closedBug95perc': 'Медианное значение времени закрытия 95 % bug-вопросов, '
                           'среди всех закрытых bug-вопросов (int дней)',
        'closedBug50perc': 'Медианное значение времени закрытия bug-вопросов, '
                           'среди всех закрытых bug-вопросов (int дней)',
    },
    'error': {
        'errorDescription': 'Описание ошибки (str)',
        'errorMessage': 'Текст ошибки (str)',
    },
    'meta': {
        'code': 'Код ответа (int)',
        'information': 'Информация о запросе (str)',
        'cost': 'Стоимость запроса (int)',
        'remains': 'Остаток кредитов для запросов (int 5000/час)',
        'resetAt': 'Время обнуления кредитов (str iso)',
        'estimatedTime': 'Предполагаемое время запроса (float секунд)',
        'time': 'Фактическое время запроса (float секунд)',
        'requestDowntime': 'Время простоя, ожидание ответа GitHub (float секунд)',
    },
}
