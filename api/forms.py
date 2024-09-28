from abc import ABC, abstractmethod

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Regexp

import re


class FormFactoryBase(ABC):
    def __init__(self, **kwargs):
        self._form_kwargs = kwargs

    def __getitem__(self, item):
        return self._form_kwargs[item]

    def __setitem__(self, key, value):
        self._form_kwargs[key] = value

    def __delitem__(self, key):
        del self._form_kwargs[key]

    @abstractmethod
    def __call__(self):
        pass


class CustomFormFactory(FormFactoryBase):
    def __call__(self, **kwargs):
        class CustomForm(FlaskForm):
            pass

        for field_name, field in kwargs.items():
            setattr(CustomForm, field_name, field)

        return CustomForm(**self._form_kwargs)


class EditorFormFactory(FormFactoryBase):
    def __call__(self, **kwargs):
        class EditorForm(FlaskForm):
            field_name = StringField('Field name', validators=[
                DataRequired(),
                Regexp(re.compile(r'^(?!validator)[a-z]\w*(?!\s+)$', re.IGNORECASE))
            ])
            field_type = SelectField('Field type', validators=[DataRequired()], choices=kwargs)
            add_field = SubmitField('Add field')
            remove_field = SubmitField('Remove field')

        return EditorForm(**self._form_kwargs)


class SaveFormForm(FlaskForm):
    form_name = StringField('Form name', validators=[DataRequired()])
    submit = SubmitField('Save form')


class AddFormFormFactory:
    def __init__(self, *args):
        types = ''

        for type_name in args:
            types += f'{type_name}|'
        types = types[:-1:]

        self._types = types

    def __call__(self, **kwargs):
        class AddFormForm(FlaskForm):
            form_name = StringField('Name', validators=[DataRequired()])
            form_fields = TextAreaField(
                label='Fields',
                validators=[
                    DataRequired(),
                    Regexp(
                        re.compile(
                            r'^(?!.*(\r?\n){2,}.*)(?!(\w+:\w+\r?\n)*(\w+):\w+\r?\n(\w+:\w+\r?\n)*\3:\w+(\s|$))([a-z]\w*:(' + self._types + r')\r?\n)*[a-z]\w*:(' + self._types + r')(?!\s+)$',
                            re.IGNORECASE | re.S
                        )
                    )
                ]
            )
            submit = SubmitField('Add form')

        return AddFormForm(**kwargs)
