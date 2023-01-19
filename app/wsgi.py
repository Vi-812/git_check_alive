from flask import Flask, render_template,flash
from app.forms import RepositoryPath
import requests

app_flask = Flask(__name__)
app_flask.config['SECRET_KEY'] = 'super_secret_key'


@app_flask.route('/', methods = ['GET', 'POST'])
def main_page():
    form = RepositoryPath()
    # Странная отловка сообщений
    if form.validate_on_submit():
        flash('нажато)')

    # content = requests.request().json()
    # print(content)
    return render_template('index.html', form=form)

@app_flask.errorhandler(404)
def page_not_found(error):
    return 'Страницы не существует!!', 404

if __name__ == '__main__':
    app_flask.run(port=8080)