from app import app_sanic, jinja, token_flask, forms
from sanic import HTTPResponse
from analytical import database


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
        form = forms.RepositoryPathForm()
        print(1112)
        return jinja.render('index.html', request, form=form), 200
    elif request.method == 'POST':
        form = forms.RepositoryPathForm()
        repository_path = request.form['link_repository']
        instance_db_client = database.DataBaseHandler()
        json, code = await instance_db_client.get_report(repository_path=repository_path, token=token_flask)
        return jinja.render('index.html', request, form=form, json=json), code


# @app_sanic.error_handler(404)
# async def page_not_found(error):
#     return 'Страницы не существует!!', 404
