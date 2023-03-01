from frontend import app_sanic, jinja, token_app, forms
from sanic import HTTPResponse
from backend import database
from loguru import logger


session_req = {}
@app_sanic.middleware('request')
async def add_session(request):
    request.ctx.session = session_req


@app_sanic.route('/api/repo', methods=['GET'])
async def get_api_request(request):
    repository_path = request.args.get('name')
    logger.info(f'<<< url={request.url}, repository_path={repository_path}')
    instance_db_client = database.DataBaseHandler()
    resp_json, code = await instance_db_client.get_report(repository_path=repository_path, token=token_app)
    logger.info(f'>>> url={request.url}, code={code}, resp_json={resp_json}')
    return HTTPResponse(resp_json, status=code)


@app_sanic.route('/api', methods=['POST'])
async def post_api_request(request):
    repository_path = request.json['repository_path']
    token_api = request.json['token']
    logger.info(f'<<< url={request.url}, repository_path={repository_path}')
    if not token_api:
        token_api = token_app
    instance_db_client = database.DataBaseHandler()
    resp_json, code = await instance_db_client.get_report(repository_path=repository_path, token=token_api)
    logger.info(f'>>> url={request.url}, code={code}, resp_json={resp_json}')
    return HTTPResponse(resp_json, status=code)


@app_sanic.route('/', methods=['GET'])
async def index(request):
    form = forms.RepositoryPathForm(request)
    return jinja.render('index.html', request, form=form)


@app_sanic.route('/', methods=['POST'])
async def index_resp(request):
    form = forms.RepositoryPathForm(request)
    repository_path = request.form.get(['link_repository'][0], None)
    logger.info(f'<<< url={request.url}, repository_path={repository_path}')
    if repository_path:
        instance_db_client = database.DataBaseHandler()
        resp_json, code = await instance_db_client.get_report(repository_path=repository_path, token=token_app)
    else:
        resp_json = code = None
    logger.info(f'>>> url={request.url}, code={code}, resp_json={resp_json}')
    return jinja.render('index.html', request, form=form, json=resp_json)
