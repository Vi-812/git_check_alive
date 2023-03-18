from frontend import app_sanic, jinja, token_app, forms
from backend import database
from backend.analytic import functions as fn
from backend.json_preparation import final_json_preparation
from dto.received_request import ReceivedRequest
from dto.request_response import RequestResponse
from sanic import HTTPResponse
from loguru import logger
import json

session_req = {}  # Создаем set для сессий Sanic


@app_sanic.middleware('request')
async def add_session(request):
    request.ctx.session = session_req  # Добавляем сессию в Sanic


@app_sanic.get('/')
async def index(request):
    form = forms.RepositoryPathForm(request)
    return jinja.render('index.html', request, form=form, data=None)


@app_sanic.get('/help')
async def index(request):
    return jinja.render('help.html', request)


@app_sanic.post('/')
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
            resp_json = await fn.path_error_400(rec_request=rec_request,
                                                resp_json=resp_json,
                                                repository_path=repository_path
                                                )
            resp_json, code = await final_json_preparation(rec_request=rec_request, resp_json=resp_json)
            resp_json = json.loads(resp_json)
        logger.info(f'|>>>{i_test} {code=}, rec_request={rec_request.dict(exclude={"token"})}, {resp_json=}')
        return jinja.render('index.html', request, form=form, data=resp_json)
    except Exception as e:
        return await global_error(error=e, rec_request=rec_request, resp_json=resp_json)


@app_sanic.get('/api/repo')
@app_sanic.get('/api/issues-statistic')
@app_sanic.get('/api/full')
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

@app_sanic.post('/api/repo')
@app_sanic.post('/api/issues-statistic')
@app_sanic.post('/api/full')
async def post_api_request(request):
    try:
        repository_path = request.json.get('repositoryPath', None)
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
    logger.critical(f'GLOBAL_ERROR_500! rec_request={rec_request.dict(exclude={"token"})}, {resp_json=}, {error=}')
    resp_json.meta.code = 500
    resp_json.error.description = 'Internal Server Error'
    resp_json.error.message = str(error)
    return resp_json
