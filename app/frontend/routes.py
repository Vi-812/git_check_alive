from app.core.settings import templates, token_app
from app.backend import database
from app.backend.analytic import errors_handler as eh
from app.backend.json_preparation import final_json_preparation
from app.core.data_transfer_objects.received_request import ReceivedRequest
from app.core.data_transfer_objects.answer import RequestResponse
from app.core.values_description import values_description
from app.frontend.global_error_handler import global_error
from loguru import logger
import json
from fastapi import APIRouter, Request, Response, Form


router = APIRouter()


@router.get('/')
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get('/values')
async def values(request: Request):
    return templates.TemplateResponse("values.html", {"request": request, "values_description": values_description})


@router.get('/rest-api')
async def rest_api(request: Request):
    return templates.TemplateResponse("api_help.html", {"request": request})


@router.get('/contact')
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


@router.post('/')
async def index_resp(request: Request, text: str = Form(...)):
    try:
        print(text)
        repository_path = text
        cache = request.headers.get('skipCache', False)
        i_test = request.headers.get('test', '')
        rec_request = ReceivedRequest(url=request.url.path, repo_path=repository_path, token=token_app, cache=cache)
        resp_json = RequestResponse(data={}, error={}, meta={})  # Создаем экземпляр RequestResponse
    except Exception as e:
    # except ZeroDivisionError as e:
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
        return templates.TemplateResponse("index.html", {
            "request": request,
            "status": code,
            "data": resp_json,
            "values_description": values_description,
        })
    except Exception as e:
    # except ZeroDivisionError as e:
        return await global_error(error=e, rec_request=rec_request, resp_json=resp_json)


@router.get('/api/repo')
@router.get('/api/issues-statistic')
@router.get('/api/full')
async def get_api_request(request: Request):
    try:
        repository_path = request.query_params.get('name', None)
        skip_cache = request.query_params.get('skipCache', False)
        token_api = request.headers.get('token', None)
        i_test = request.headers.get('test', '')
        if not token_api:
            token_api = token_app
        request_url = str(request.url)
        if '/api/repo' in request_url:
            response_type = 'repo'  # Запрос информации только о репозитории
        elif '/api/issues-statistic' in request_url:
            response_type = 'issues'  # Запрос информации только о issues
        else:
            response_type = 'full'  # Полный запрос

        rec_request = ReceivedRequest(
            url=request_url,
            repo_path=repository_path,
            token=token_api,
            skip_cache=skip_cache,
            response_type=response_type,
        )
        resp_json = RequestResponse(
            data={},
            error={},
            meta={},
        )

    except Exception as e:
    # except ZeroDivisionError as e:
        return await global_error(error=e)
    try:
        logger.info(f'<<<|{i_test} rec_request={rec_request.dict(exclude={"token"})}')

        instance_db_client = database.DataBaseHandler()
        resp_json, code = await instance_db_client.get_report(rec_request=rec_request, resp_json=resp_json)

        logger.info(f'|>>>{i_test} {code=}, rec_request={rec_request.dict(exclude={"token"})}, {resp_json=}')

        return Response(content=resp_json, status_code=code)
    except Exception as e:
    # except ZeroDivisionError as e:
        return await global_error(error=e, rec_request=rec_request, resp_json=resp_json)


@router.post('/api/repo')
@router.post('/api/issues-statistic')
@router.post('/api/full')
async def post_api_request(request: Request):
    try:
        data = await request.json()
        repository_path = data.get('name', None)
        token_api = data.get('token', None)
        skip_cache = data.get('skipCache', False)
        i_test = request.headers.get('test', '')
        if not token_api:
            token_api = token_app
        request_url = str(request.url)
        if '/api/repo' in request_url:
            response_type = 'repo'  # Запрос информации только о репозитории
        elif '/api/issues-statistic' in request_url:
            response_type='issues'  # Запрос информации только о issues
        else:
            response_type='full'  # Полный запрос

        rec_request = ReceivedRequest(
            url=request_url,
            repo_path=repository_path,
            token=token_api,
            skip_cache=skip_cache,
            response_type=response_type,
        )
        resp_json = RequestResponse(
            data={},
            error={},
            meta={},
        )

    except Exception as e:
    # except ZeroDivisionError as e:
        return await global_error(error=e)
    try:
        logger.info(f'<<<|{i_test} rec_request={rec_request.dict(exclude={"token"})}')

        instance_db_client = database.DataBaseHandler()
        resp_json, code = await instance_db_client.get_report(rec_request=rec_request, resp_json=resp_json)

        logger.info(f'|>>>{i_test} {code=}, rec_request={rec_request.dict(exclude={"token"})}, {resp_json=}')

        return Response(content=resp_json, status_code=code)
    except Exception as e:
    # except ZeroDivisionError as e:
        return await global_error(error=e, rec_request=rec_request, resp_json=resp_json)
