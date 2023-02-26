from sanic_wtf import SanicForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired

from wtforms import Form, StringField, TextAreaField, SelectField, validators, SubmitField

class RepositoryPathForm(SanicForm):
    link_repository = StringField('Введите ссылку на репозиторий')
    submit_path = SubmitField('Анализировать')
