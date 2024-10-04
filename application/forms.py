from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import HiddenField, TextAreaField
from wtforms.validators import InputRequired, Regexp, Length

import re


def create_form(fields, *args, **kwargs):
    class CustomForm(FlaskForm): pass

    for field_name, field in fields.items():
        setattr(CustomForm, field_name, field)

    return CustomForm(*args, **kwargs)


def create_editor(choices, *args, **kwargs):
    class EditorForm(FlaskForm):
        field_name = StringField('Field name', validators=[
            Regexp(re.compile(r'^(?!validator)[a-z]\w*(?!\s+)$|^$', re.IGNORECASE))
        ])
        field_label = StringField('Field label')
        field_type = SelectField('Field type', validators=[InputRequired()], choices=choices, validate_choice=False)
        add_field = SubmitField('Add field')
        remove_field = SubmitField('Remove field')

    return EditorForm(*args, **kwargs)


class ImageForm(FlaskForm):
    obj_type = HiddenField(default='image')
    source = FileField('', validators=[FileRequired(), FileAllowed(['png', 'jpg'])])


class HTMLForm(FlaskForm):
    obj_type = HiddenField(default='html')
    source = TextAreaField('', validators=[InputRequired()])


class SaveFormForm(FlaskForm):
    form_label = StringField('Form label', validators=[
        InputRequired(),
        Regexp(re.compile(r'^(\w|\w[\w ]*\w)(?!\s+)$', re.IGNORECASE))
    ])
    doc_form = FileField('Template', validators=[FileAllowed(['docx'])])
    save_form = SubmitField('Save form')
    delete_form = SubmitField('Delete form')


class SelectFieldEditor(FlaskForm):
    choice_name = StringField('Choice name', validators=[InputRequired()])
    add_choice = SubmitField('Add choice')
    remove_choice = SubmitField('Remove choice')


class SaveSelectField(FlaskForm):
    field_label = StringField('Field label', validators=[InputRequired(), Length(min=5)])
    save_field = SubmitField('Save field')
    delete_field = SubmitField('Delete field')
