from flask import request, render_template
from app import app_flask, token_flask, forms
from analytical import database


@app_flask.route('/api', methods=['POST'])
async def api_request():
    token_api = request.json['token']
    repository_path = request.json['repository_path']
    instance_db_client = database.DataBaseHandler()
    return await instance_db_client.get_report(repository_path=repository_path, token=token_api)


@app_flask.route('/', methods=['GET', 'POST'])
async def main_page():
    if request.method == 'GET':
        form = forms.RepositoryPathForm()
        return render_template('index.html', form=form), 200
    elif request.method == 'POST':
        form = forms.RepositoryPathForm()
        repository_path = request.form['link_repository']
        instance_db_client = database.DataBaseHandler()
        json, code = await instance_db_client.get_report(repository_path=repository_path, token=token_flask)
        return render_template('index.html', form=form, json=json), code


@app_flask.errorhandler(404)
async def page_not_found(error):
    return 'Страницы не существует!!', 404
