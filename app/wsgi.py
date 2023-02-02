import json
from flask import render_template, request
from app.forms import RepositoryPathForm
from app import app_flask, token_flask, database
from req_response import resp_json


@app_flask.route('/api', methods=['POST'])
def api_request():
    token_api = request.json['token']
    repository_path = request.json['repository_path']
    instance_db_client = database.DataBaseHandler()
    instance_db_client.get_report(repository_path, token_api)
    code = resp_json.query_info.code
    return resp_json.json(), code


@app_flask.route('/', methods=['GET', 'POST'])
def main_page():
    if request.method == 'GET':
        form = RepositoryPathForm()
        return render_template('index.html', form=form), 200
    elif request.method == 'POST':
        form = RepositoryPathForm()
        repository_path = request.form['link_repository']
        instance_db_client = database.DataBaseHandler()
        instance_db_client.get_report(repository_path, token_flask)
        code = resp_json.query_info.code
        return render_template('index.html', form=form, json=resp_json.json()), code


@app_flask.errorhandler(404)
def page_not_found(error):
    return 'Страницы не существует!!', 404


if __name__ == '__main__':
    app_flask.run(port=8080, debug=False)
