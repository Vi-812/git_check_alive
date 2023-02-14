from app import app_flask
from flask import request, render_template
from app import token_flask, database, forms
from req_response import resp_json
import asyncio
import aiohttp


@app_flask.route('/api', methods=['POST'])
def api_request():
    token_api = request.json['token']
    repository_path = request.json['repository_path']
    instance_db_client = database.DataBaseHandler()
    instance_db_client.get_report(repository_path, token_api)
    code = resp_json.query_info.code
    if code != 200:
        resp_json.__delattr__('repository_info')
        resp_json.__delattr__('analytic')
    return resp_json.json(by_alias=True), code


@app_flask.route('/', methods=['GET', 'POST'])
async def main_page():
    session = aiohttp.ClientSession()
    print(session.__dict__)
    if request.method == 'GET':
        form = forms.RepositoryPathForm()
        return render_template('index.html', form=form), 200
    elif request.method == 'POST':
        form = forms.RepositoryPathForm()
        repository_path = request.form['link_repository']
        instance_db_client = database.DataBaseHandler()
        instance_db_client.get_report(repository_path, token_flask)
        code = resp_json.query_info.code
        if code != 200:
            resp_json.__delattr__('repository_info')
            resp_json.__delattr__('analytic')
        return render_template('index.html', form=form, json=resp_json.json(by_alias=True)), code


@app_flask.errorhandler(404)
def page_not_found(error):
    return 'Страницы не существует!!', 404