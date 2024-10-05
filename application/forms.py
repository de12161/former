from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.validators import InputRequired, Regexp

import re


def create_form(fields, *args, **kwargs):
    class CustomForm(FlaskForm): pass

    for field_name, field in fields.items():
        setattr(CustomForm, field_name, field)

    return CustomForm(*args, **kwargs)


def create_editor(choices, *args, **kwargs):
    class EditorForm(FlaskForm):
        field_name = StringField('Идентификатор поля', validators=[
            Regexp(re.compile(r'^(?!validator|csrf_token)[a-z]\w*(?!\s+)$|^$', re.IGNORECASE), message='Неверный идентификатор поля')
        ])
        field_label = StringField('Название поля')
        field_type = SelectField('Тип поля', validators=[InputRequired(message='Тип поля обязателен')], choices=choices, validate_choice=False)
        add_field = SubmitField('Добавить поле')
        remove_field = SubmitField('Убрать поле')

    return EditorForm(*args, **kwargs)


class SaveFormForm(FlaskForm):
    form_label = StringField('Название формы', validators=[
        Regexp(re.compile(r'^([\wа-я]|[\wа-я][\w а-я]*[\wа-я])(?!\s+)$', re.IGNORECASE), message='Неверное название формы')
    ])
    doc_form = FileField('Шаблон', validators=[FileAllowed(['docx'], message='Формат шаблона должен быть .docx')])
    save_form = SubmitField('Сохранить форму')
    delete_form = SubmitField('Удалить форму')


class SelectFieldEditor(FlaskForm):
    choice_name = StringField('Название опции', validators=[InputRequired(message='Опция должна иметь название')])
    add_choice = SubmitField('Добавить опцию')
    remove_choice = SubmitField('Убрать опцию')


class SaveSelectField(FlaskForm):
    field_label = StringField('Название поля', validators=[InputRequired(message='Поле должно иметь название'), Regexp(re.compile(r'^.*[^0-9].*$'), message='Название поля не может состоять полностью из цифр')])
    save_field = SubmitField('Сохранить поле')
    delete_field = SubmitField('Удалить поле')
