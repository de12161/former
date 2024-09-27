import re

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Regexp


class CustomFormFactory:
    def __init__(self, **kwargs):
        self.field_types = kwargs

    def __call__(self, *args, **kwargs):
        class CustomForm(FlaskForm):
            pass

        for name in args:
            setattr(CustomForm, name, self.field_types[name](**kwargs))

        return CustomForm()


class AddFormFormFactory:
    def __init__(self, *args, **kwargs):
        types = ''

        for name in args or kwargs.keys():
            types += f'{name}|'
        types = types[:-1:]

        self._types = types

    def __call__(self, *args, **kwargs):
        class AddFormForm(FlaskForm):
            form_name = StringField('Name', validators=[DataRequired()])
            form_fields = TextAreaField(
                label='Fields',
                validators=[
                    DataRequired(),
                    Regexp(
                        re.compile(
                            r'^(?!.*(\r?\n){2,}.*)(?!([\w_]+:\w+\r?\n)*([\w_]+):\w+\r?\n([\w_]+:\w+\r?\n)*\2:\w+(\s|$))([a-z_][\w_]*:(' + self._types + r')\r?\n)*[a-z_][\w_]*:(' + self._types + r')(?!\s+)$',
                            re.IGNORECASE | re.S
                        )
                    )
                ]
            )
            submit = SubmitField('Add form')

        return AddFormForm(*args, **kwargs)
