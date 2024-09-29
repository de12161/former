from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired, Regexp

import re


def create_form_class(**fields):
    class CustomForm(FlaskForm): pass

    for field_name, field in fields.items():
        setattr(CustomForm, field_name, field)

    return CustomForm


def create_editor_class(**choices):
    class EditorForm(FlaskForm):
        field_name = StringField('Field name', validators=[
            DataRequired(),
            Regexp(re.compile(r'^(?!validator)[a-z]\w*(?!\s+)$', re.IGNORECASE))
        ])
        field_type = SelectField('Field type', validators=[DataRequired()], choices=choices)
        add_field = SubmitField('Add field')
        remove_field = SubmitField('Remove field')

    return EditorForm


class SaveFormForm(FlaskForm):
    form_name = StringField('Form name', validators=[
        DataRequired(),
        Regexp(re.compile(r'^(\w|\w[\w ]*\w)(?!\s+)$', re.IGNORECASE))
    ])
    submit = SubmitField('Save form')
