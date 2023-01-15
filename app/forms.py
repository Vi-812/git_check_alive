from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired



class RepositoryPath(FlaskForm):
    # class Meta:
    #     csrf = False
    link = StringField('Введите ссылку на репозиторий', validators=[DataRequired()])
    submit = SubmitField('Анализировать')