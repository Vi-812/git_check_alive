from fastapi import FastAPI, Request

from .values_description import values_description




from frontend import app, templates, token_app, forms
from backend import database
from backend.analytic import errors_handler as eh
from backend.json_preparation import final_json_preparation
from dto.received_request import ReceivedRequest
from dto.request_response import RequestResponse
from sanic import HTTPResponse
from loguru import logger
import json
# from sanic_cors import CORS
# CORS(app_sanic)


from starlette import status
from starlette.responses import Response
# from models import Body

session_req = {}  # Создаем set для сессий Sanic


# @app_sanic.middleware('request')
# async def add_session(request):
#     request.ctx.session = session_req  # Добавляем сессию в Sanic


@app.get('/')
async def index(request):
    form = forms.RepositoryPathForm(request)
    return templates.render('index.html', request, form=form, data=None)


@app.get('/values')
async def values(request):
    return templates.render('values.html', request, values_description=values_description)


@app.get('/rest-api')
async def rest_api(request):
    return templates.render('api_help.html', request)


@app.get('/contact')
async def contact(request):
    return templates.render('contact.html', request)


@app.post('/')
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


@app.get('/api/repo')
@app.get('/api/issues-statistic')
@app.get('/api/full')
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


from typing import Any, Dict, List, Union

@app.post('/api/repo')
@app.post('/api/issues-statistic')
@app.post('/api/full')
async def post_api_request(request: Request=None):
    try:
        repository_path = request.get('name', None)
        token_api = request.get('token', None)
        skip_cache = request.get('skipCache', False)
        i_test = request.headers.get('test', '')
        print(f'SS_{repository_path=}, {token_api=}')
        xxx=request.url
        yyy=xxx.path
        print(f'22_{xxx=}')
        print(f'22_{yyy=}')
        if not token_api:
            token_api = token_app
        if '/api/repo' in request.url.path:
            response_type = 'repo'  # Запрос информации только о репозитории
        elif '/api/issues-statistic' in request.url.path:
            response_type='issues'  # Запрос информации только о issues
        else:
            response_type='full'  # Полный запрос
        rec_request = ReceivedRequest(url=request.url.path, repo_path=repository_path, token=token_api,
                                      skip_cache=skip_cache,response_type=response_type)
        resp_json = RequestResponse(data={}, error={}, meta={})  # Создаем экземпляр RequestResponse
    # except Exception as e:
    except ZeroDivisionError as e:
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
    # Глобальный обработчик ошибок для всех непредвиденных ситуаций
    if not rec_request:
        logger.critical(f'GLOBAL_ERROR_500! {error=}, {resp_json=}')
    else:
        logger.critical(f'GLOBAL_ERROR_500! {error=}, rec_request={rec_request.dict(exclude={"token"})}, {resp_json=}')
    resp_json.meta.code = 500
    resp_json.error.error_description = 'Internal Server Error'
    resp_json.error.error_message = str(error)
    return resp_json
