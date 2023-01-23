from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class RepositoryPath(FlaskForm):
    link = StringField('Введите ссылку на репозиторий')
    submit = SubmitField('Анализировать')