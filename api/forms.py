import re

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Regexp


class CustomFormFactory:
    def __init__(self, **kwargs):
        self.form_kwargs = kwargs

    def __call__(self, **kwargs):
        class CustomForm(FlaskForm):
            pass

        for field_name, field in kwargs.items():
            setattr(CustomForm, field_name, field)

        return CustomForm(**self.form_kwargs)


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
