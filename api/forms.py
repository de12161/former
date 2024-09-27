import re

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Regexp


class CustomFormFactory:
    def __init__(self, field_types, form_kwargs=None):
        if form_kwargs is None:
            form_kwargs = {}
        self.field_types = field_types
        self.form_kwargs = form_kwargs

    def __call__(self, **kwargs):
        class CustomForm(FlaskForm):
            pass

        index = 0
        for field_name, field_kwargs in kwargs.items():
            if 'id' not in field_kwargs.keys():
                field_kwargs['id'] = f'{field_name}-{index}'
                index += 1
            setattr(CustomForm, field_name, self.field_types[field_kwargs['type']](**field_kwargs.get('kwargs')))

        if not hasattr(CustomForm, 'submit'):
            setattr(CustomForm, 'submit', SubmitField('Submit'))

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
                            r'^(?!.*(\r?\n){2,}.*)(?!([\w_]+:\w+\r?\n)*([\w_]+):\w+\r?\n([\w_]+:\w+\r?\n)*\2:\w+(\s|$))([a-z_][\w_]*:(' + self._types + r')\r?\n)*[a-z_][\w_]*:(' + self._types + r')(?!\s+)$',
                            re.IGNORECASE | re.S
                        )
                    )
                ]
            )
            submit = SubmitField('Add form')

        return AddFormForm(**kwargs)
