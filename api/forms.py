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
    form_name = StringField('Form name', validators=[
        DataRequired(),
        Regexp(re.compile(r'^(\w|\w[\w ]*\w)(?!\s+)$', re.IGNORECASE))
    ])
    submit = SubmitField('Save form')
