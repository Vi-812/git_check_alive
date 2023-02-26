from frontend import app_sanic, jinja, token_app, forms
from sanic import HTTPResponse
from backend import database


session = {}
@app_sanic.middleware('request')
async def add_session(request):
    request.ctx.session = session


@app_sanic.route('/api', methods=['POST'])
async def api_request(request):
    token_api = request.json['token']
    repository_path = request.json['repository_path']
    instance_db_client = database.DataBaseHandler()
    resp_json, code = await instance_db_client.get_report(repository_path=repository_path, token=token_api)
    return HTTPResponse(resp_json, status=code)


@app_sanic.route('/', methods=['GET'])
async def index(request):
    form = forms.RepositoryPathForm(request)
    return jinja.render('index.html', request, form=form)


@app_sanic.route('/', methods=['POST'])
async def index_resp(request):
    form = forms.RepositoryPathForm(request)
    repository_path = request.form.get(['link_repository'][0], None)
    if repository_path:
        instance_db_client = database.DataBaseHandler()
        json, code = await instance_db_client.get_report(repository_path=repository_path, token=token_app)
    else:
        json = None
    return jinja.render('index.html', request, form=form, json=json)
