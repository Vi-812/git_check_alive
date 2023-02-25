from wtforms import Form, StringField, TextAreaField, SelectField, validators, SubmitField

class RepositoryPathForm(Form):
    link_repository = StringField('Введите ссылку на репозиторий')
    submit_path = SubmitField('Анализировать')
