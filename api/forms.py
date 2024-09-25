from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired


class TestForm(FlaskForm):
    text = StringField('Text', validators=[DataRequired()])
    template = FileField('Template', validators=[DataRequired()])
    submit = SubmitField('Submit')


class DynamicForm(FlaskForm): pass


class AddFormForm(FlaskForm):
    submit = SubmitField('Add form')
