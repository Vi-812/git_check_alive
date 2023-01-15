from flask import Flask, render_template
from app.forms import RepositoryPath


app_flask = Flask(__name__)


@app_flask.route('/')
def main_page():
    form = RepositoryPath()
    return render_template('index.html', form=form)

@app_flask.errorhandler(404)
def page_not_found(error):
    return 'Страницы не существует!!', 404

if __name__ == '__main__':
    app_flask.run(port=8080)