from app import app_sanic, jinja, token_app, forms
from sanic import HTTPResponse
from analytical import database


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


@app_sanic.route('/', methods=['GET', 'POST'])
async def main_page(request):
    if request.method == 'GET':
        form = forms.RepositoryPathForm(request)
        return jinja.render('index.html', request, form=form)
    elif request.method == 'POST':
        form = forms.RepositoryPathForm(request)
        repository_path = request.form['link_repository'][0]
        instance_db_client = database.DataBaseHandler()
        json, code = await instance_db_client.get_report(repository_path=repository_path, token=token_app)
        return jinja.render('index.html', request, form=form, json=json)
