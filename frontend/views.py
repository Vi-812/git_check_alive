from frontend import app_sanic, jinja, token_app, forms
from frontend.json_preparation import final_json_preparation
from backend import database
from dto.received_request import ReceivedRequest
from sanic import HTTPResponse
from loguru import logger

session_req = {}


@app_sanic.middleware('request')
async def add_session(request):
    request.ctx.session = session_req


@app_sanic.route('/', methods=['GET'])
async def index(request):
    form = forms.RepositoryPathForm(request)
    return jinja.render('index.html', request, form=form)


@app_sanic.route('/', methods=['POST'])
async def index_resp(request):
    form = forms.RepositoryPathForm(request)
    repository_path = request.form.get(['link_repository'][0], None)
    cache = request.headers.get('cache', True)
    i_test = request.headers.get('test', '')
    rec_request = ReceivedRequest(url=request.url, repo_path=repository_path, token=token_app, cache=cache)
    logger.info(f'<<<|{i_test} rec_request={rec_request.dict(exclude={"token"})}')
    if repository_path:
        instance_db_client = database.DataBaseHandler()
        resp_json = await instance_db_client.get_report(rec_request=rec_request)
        resp_json, code = await final_json_preparation(resp_json)
    else:
        resp_json = "Bad repository adress, enter the address in the format " \
                    "'https://github.com/Vi-812/git_check_alive' or 'vi-812/git_check_alive'."
        code = 400
    logger.info(f'|>>>{i_test} code={code}, rec_request={rec_request.dict(exclude={"token"})}, resp_json={resp_json}')
    return jinja.render('index.html', request, form=form, json=resp_json)


@app_sanic.route('/api/repo', methods=['GET'])
@app_sanic.route('/api/issues-statistic', methods=['GET'])
async def get_api_request(request):
    repository_path = request.args.get('name', None)
    cache = request.args.get('cache', True)
    token_api = request.headers.get('token', None)
    i_test = request.headers.get('test', '')
    if not token_api:
        token_api = token_app
    if '/api/repo' in request.url:
        rec_request = ReceivedRequest(url=request.url, repo_path=repository_path, token=token_api, cache=cache,
                                      response_type='repo')
    elif '/api/issues-statistic' in request.url:
        rec_request = ReceivedRequest(url=request.url, repo_path=repository_path, token=token_api, cache=cache,
                                      response_type='full')
    logger.info(f'<<<|{i_test} rec_request={rec_request.dict(exclude={"token"})}')
    instance_db_client = database.DataBaseHandler()
    resp_json = await instance_db_client.get_report(rec_request=rec_request)
    resp_json, code = await final_json_preparation(resp_json)
    logger.info(f'|>>>{i_test} code={code}, rec_request={rec_request.dict(exclude={"token"})}, resp_json={resp_json}')
    return HTTPResponse(resp_json, status=code)


@app_sanic.route('/api/repo', methods=['POST'])
@app_sanic.route('/api/issues-statistic', methods=['POST'])
async def post_api_request(request):
    repository_path = request.json['repository_path']
    token_api = request.json['token']
    cache = request.headers.get('cache', True)
    i_test = request.headers.get('test', '')
    if not token_api:
        token_api = token_app
    if '/api/repo' in request.url:
        rec_request = ReceivedRequest(url=request.url, repo_path=repository_path, token=token_api, cache=cache,
                                      response_type='repo')
    elif '/api/issues-statistic' in request.url:
        rec_request = ReceivedRequest(url=request.url, repo_path=repository_path, token=token_api, cache=cache,
                                      response_type='full')
    logger.info(f'<<<|{i_test} rec_request={rec_request.dict(exclude={"token"})}')
    instance_db_client = database.DataBaseHandler()
    resp_json = await instance_db_client.get_report(rec_request=rec_request)
    resp_json, code = await final_json_preparation(resp_json)
    logger.info(f'|>>>{i_test} code={code}, rec_request={rec_request.dict(exclude={"token"})}, resp_json={resp_json}')
    return HTTPResponse(resp_json, status=code)
