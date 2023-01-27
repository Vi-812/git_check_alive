from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class RepositoryPathForm(FlaskForm):
    link_repository = StringField('Введите ссылку на репозиторий')
    submit_path = SubmitField('Анализировать')