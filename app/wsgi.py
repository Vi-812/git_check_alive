from flask import Flask, render_template, request, jsonify
from app.forms import RepositoryPath
import github_api_client


app_flask = Flask(__name__)
app_flask.config['SECRET_KEY'] = 'super_secret_key'


@app_flask.route('/api', methods=['POST'])
def api_request():
    token = request.json['token']
    repository_path = request.json['repository_path']

    instance_api_client = github_api_client.GithubApiClient(token)
    instance_api_client.push_repository(repository_path)
    print('++')
    return_json = instance_api_client.get_json()
    print(return_json)
    return return_json


@app_flask.route('/', methods=['GET', 'POST'])
def main_page():
    form = RepositoryPath()
    # Доработать форму
    return render_template('index.html', form=form)


@app_flask.errorhandler(404)
def page_not_found(error):
    return 'Страницы не существует!!', 404


if __name__ == '__main__':
    app_flask.run(port=8080, debug=True)