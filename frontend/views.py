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
    rec_request = ReceivedRequest(url=request.url, repo_path=repository_path, token=token_app)
    logger.info(f'<<<| rec_request={rec_request.dict(exclude={"token"})}')
    if repository_path:
        instance_db_client = database.DataBaseHandler()
        resp_json = await instance_db_client.get_report(rec_request=rec_request)
        resp_json, code = await final_json_preparation(resp_json)
    else:
        resp_json = "Bad repository adress, enter the address in the format " \
                    "'https://github.com/Vi-812/git_check_alive' or 'vi-812/git_check_alive'."
        code = 400
    logger.info(f'|>>> code={code}, rec_request={rec_request.dict(exclude={"token"})}, resp_json={resp_json}')
    return jinja.render('index.html', request, form=form, json=resp_json)


@app_sanic.route('/api/repo', methods=['GET'])
async def get_api_request(request):
    repository_path = request.args.get('name', None)
    token_api = request.headers.get('token', None)
    if not token_api:
        token_api = token_app
    rec_request = ReceivedRequest(url=request.url, repo_path=repository_path, token=token_api)  # type!!!
    logger.info(f'<<<| rec_request={rec_request.dict(exclude={"token"})}')
    instance_db_client = database.DataBaseHandler()
    resp_json = await instance_db_client.get_report(rec_request=rec_request)
    resp_json, code = await final_json_preparation(resp_json)
    logger.info(f'|>>> code={code}, rec_request={rec_request.dict(exclude={"token"})}, resp_json={resp_json}')
    return HTTPResponse(resp_json, status=code)


@app_sanic.route('/api', methods=['POST'])
async def post_api_request(request):
    repository_path = request.json['repository_path']
    token_api = request.json['token']
    if not token_api:
        token_api = token_app
    rec_request = ReceivedRequest(url=request.url, repo_path=repository_path, token=token_api)  # type!!!
    logger.info(f'<<<| rec_request={rec_request.dict(exclude={"token"})}')
    instance_db_client = database.DataBaseHandler()
    resp_json = await instance_db_client.get_report(rec_request=rec_request)
    resp_json, code = await final_json_preparation(resp_json)
    logger.info(f'|>>> code={code}, rec_request={rec_request.dict(exclude={"token"})}, resp_json={resp_json}')
    return HTTPResponse(resp_json, status=code)
