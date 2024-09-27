import re

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.fields.form import FormField
from wtforms.fields.list import FieldList
from wtforms.fields.simple import TextAreaField, MultipleFileField
from wtforms.validators import DataRequired, Regexp


"""
    form_name and form_fields accept only valid variable names
    (no numbers at starting position, only characters allowed are a-z, 0-9 and '_')
    form_fields also checks for duplicates and has types (text, img and html) separated by ':'
    example:
    var:text
    var2:html
    var_img:img
"""
class FormCreator:
    class __FieldTypes:
        def __init__(self, **kwargs):
            self.__field_types = kwargs
            self.__type_str = ''
            for name in kwargs.keys():
                self.__type_str += f'{name}|'
                self.__type_str = self.__type_str[:-1:]

        def __getitem__(self, item):
            return self.__field_types[item]

        def type_str(self):
            return self.__type_str


    def __init__(self, **kwargs):
        self.field_types = FormCreator.__FieldTypes(**kwargs)

        class AddFormForm(FlaskForm):
            form_name = StringField('Name', validators=[DataRequired(), Regexp(re.compile(r'^[a-z_]+[\w_]*(?!\s+)$', re.IGNORECASE))])
            form_fields = TextAreaField(
                              label='Fields',
                              validators=[
                                  DataRequired(),
                                  Regexp(
                                          re.compile(
                                              r'^(?!.*(\r?\n){2,}.*)(?!([\w_]+:\w+\r?\n)*([\w_]+):\w+\r?\n([\w_]+:\w+\r?\n)*\2:\w+(\s|$))([a-z_][\w_]*:(' + self.field_types.type_str() + r')\r?\n)*[a-z_][\w_]*:(' + self.field_types.type_str() + r')(?!\s+)$',
                                              re.IGNORECASE | re.S
                                          )
                                      )
                              ]
                          )
            submit = SubmitField('Add form')

    def create_form(self, *args):
        class CustomForm(FlaskForm):
            pass

        for name in args:
            setattr(CustomForm, name, self.field_types[name])

        return CustomForm()
