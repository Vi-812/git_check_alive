from sanic_wtf import SanicForm
from wtforms import StringField, SubmitField

class RepositoryPathForm(SanicForm):
    link_repository = StringField('Введите ссылку на репозиторий')
    submit_path = SubmitField('Анализировать')
