import re

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.fields.form import FormField
from wtforms.fields.list import FieldList
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Regexp


class TestForm(FlaskForm):
    text = StringField('Text', validators=[DataRequired()])
    template = FileField('Template', validators=[DataRequired()])
    submit = SubmitField('Submit')


class VarEntryForm(FlaskForm):
    value = StringField('', validators=[DataRequired()])


class CustomForm(FlaskForm):
    fields = FieldList(FormField(VarEntryForm))
    # doc_form = FileField('Template:', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AddFormForm(FlaskForm):
    fields = TextAreaField('Fields',
                           validators=[
                               DataRequired(),
                               Regexp(re.compile(r'^(?!.*(\r?\n){2,}.*)[a-z_]+[\r\n\w_]*[\w_]+(?!.*(\r?\n))$', re.IGNORECASE | re.S))
                           ])
    submit = SubmitField('Add form')
