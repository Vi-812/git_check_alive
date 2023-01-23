from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class RepositoryPath(FlaskForm):
    link = StringField('Введите ссылку на репозиторий', validators=[DataRequired()])
    submit = SubmitField('Анализировать')