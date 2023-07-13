from wtforms import Form, StringField, SubmitField, validators
from wtforms.validators import DataRequired


class RepositoryPathForm(Form):
    link_repository = StringField('Введите ссылку на репозиторий', validators=[DataRequired()])
    submit_path = SubmitField('Анализ')
