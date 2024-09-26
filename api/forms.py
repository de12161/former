import re

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.fields.form import FormField
from wtforms.fields.list import FieldList
from wtforms.fields.simple import TextAreaField, MultipleFileField
from wtforms.validators import DataRequired, Regexp


class TestForm(FlaskForm):
    text = StringField('Text', validators=[DataRequired()])
    template = FileField('Template', validators=[DataRequired()])
    submit = SubmitField('Submit')


class StrVarEntryForm(FlaskForm):
    value = StringField('', validators=[DataRequired()])


class ImgVarEntryForm(FlaskForm):
    value = MultipleFileField('', validators=[DataRequired()])


class HTMLVarEntryForm(FlaskForm):
    value = TextAreaField('', validators=[DataRequired()])


class CustomForm(FlaskForm):
    text_fields = FieldList(FormField(StrVarEntryForm))
    img_fields = FieldList(FormField(ImgVarEntryForm))
    html_fields = FieldList(FormField(HTMLVarEntryForm))
    # doc_form = FileField('Template:', validators=[DataRequired()])
    submit = SubmitField('Submit')


"""
    form_name and form_fields accept only valid variable names
    (no numbers at starting position, only characters allowed are a-z, 0-9 and '_')
    form_fields also checks for duplicates and has types (text, img and html) separated by ':'
    example:
    var:text
    var2:html
    var_img:img
"""
class AddFormForm(FlaskForm):
    form_name = StringField('Name', validators=[DataRequired(), Regexp(re.compile(r'^[a-z_]+[\w_]*(?!\s+)$', re.IGNORECASE))])
    form_fields = TextAreaField('Fields',
                           validators=[
                               DataRequired(),
                               Regexp(re.compile(r'^(?!.*\s{2,}.*)(?!([\w_]+:\w+\r?\n)*([\w_]+):\w+\r?\n([\w_]+:\w+\r?\n)*\2:\w+(\s|$))([a-z_][\w_]*:(text|img|html)\r?\n)*[a-z_][\w_]*:(text|img|html)(?!\s+)$', re.IGNORECASE | re.S))
                           ])
    submit = SubmitField('Add form')
