from flask import render_template, request
from app.forms import RepositoryPathForm
import json
import github_api_client
from app import app_flask, token_flask


@app_flask.route('/api', methods=['POST'])
def api_request():
    token_api = request.json['token']
    repository_path = request.json['repository_path']
    instance_api_client = github_api_client.GithubApiClient(token_api)
    return_json = instance_api_client.get_report(repository_path)
    code = return_json['code']
    return json.dumps(return_json), code


@app_flask.route('/', methods=['GET', 'POST'])
def main_page():
    if request.method == 'GET':
        form = RepositoryPathForm()
        return render_template('index.html', form=form), 200
    elif request.method == 'POST':
        form = RepositoryPathForm()
        repository_path = request.form['link_repository']
        instance_api_client = github_api_client.GithubApiClient(token_flask)
        return_json = instance_api_client.get_report(repository_path)
        code = return_json['code']
        return render_template('index.html', form=form, json=json.dumps(return_json)), code






@app_flask.errorhandler(404)
def page_not_found(error):
    return 'Страницы не существует!!', 404


if __name__ == '__main__':
    app_flask.run(port=8080, debug=False)