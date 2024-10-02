from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired, Regexp

import re


def create_form(fields, *args, **kwargs):
    class CustomForm(FlaskForm): pass

    for field_name, field in fields.items():
        setattr(CustomForm, field_name, field)

    return CustomForm(*args, **kwargs)


def create_editor(choices, *args, **kwargs):
    class EditorForm(FlaskForm):
        field_name = StringField('Field name', validators=[
            DataRequired(),
            Regexp(re.compile(r'^(?!validator)[a-z]\w*(?!\s+)$', re.IGNORECASE))
        ])
        field_label = StringField('Field label', validators=[DataRequired()])
        field_type = SelectField('Field type', validators=[DataRequired()], choices=choices)
        add_field = SubmitField('Add field')
        remove_field = SubmitField('Remove field')

    return EditorForm(*args, **kwargs)


class SaveFormForm(FlaskForm):
    form_name = StringField('Form label', validators=[
        DataRequired(),
        Regexp(re.compile(r'^(\w|\w[\w ]*\w)(?!\s+)$', re.IGNORECASE))
    ])
    doc_form = StringField('doc', validators=[DataRequired()])
    submit = SubmitField('Save form')


class SelectFieldEditor(FlaskForm):
    choice_name = StringField('Choice name', validators=[DataRequired()])
    add_choice = SubmitField('Add choice')
    remove_choice = SubmitField('Remove choice')


class SaveSelectField(FlaskForm):
    field_label = StringField('Field label', validators=[DataRequired()])
    submit = SubmitField('Save field')
