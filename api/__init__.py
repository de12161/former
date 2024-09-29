from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap5

from flask_wtf import CSRFProtect
from wtforms.fields.simple import StringField, FileField, TextAreaField, BooleanField
from wtforms.validators import DataRequired

from .forms import CustomFormFactory, EditorFormFactory, SaveFormForm
from enum import IntEnum, auto

from secrets import token_urlsafe

key = token_urlsafe(16)

app = Flask(__name__)
app.secret_key = key

bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)

custom_factory = CustomFormFactory()
editor_factory = EditorFormFactory()


class FieldType(IntEnum):
    Bool = auto()
    Text = auto()
    TextArea = auto()
    File = auto()


field_cls = {
    FieldType.Bool: BooleanField,
    FieldType.Text: StringField,
    FieldType.TextArea: TextAreaField,
    FieldType.File: FileField
}

form_list = {}

field_list = {
    'Pre-defined fields': [
        (FieldType.Bool.value, 'Checkbox'),
        (FieldType.Text.value, 'Text Field'),
        (FieldType.TextArea.value, 'Text Area'),
        (FieldType.File.value, 'File Field')
    ],

    'Custom select fields': []
}


@app.get('/')
def index_get():
    return render_template('index.html', forms=form_list)


@app.post('/')
def index_post():
    print('POST request received:')
    for k, v in request.form.items():
        print(f'{k} = {v}')
    print(f'Form: {request.form}')
    return 'Request successful'


@app.route('/add-form', methods=['GET', 'POST'])
def add_form():
    editor = editor_factory(**field_list)
    save = SaveFormForm()
    custom_form = custom_factory()

    if request.method == 'GET':
        return render_template('add_form.html', preview=custom_form, editor=editor, save=save)


    if editor.is_submitted():
        print(f'Request: {request.form}')


    if save.submit.data and save.validate():
        print('Form saved (not really)')
        save.form_name.data = ''
        return render_template('add_form.html', preview=custom_form, editor=editor, save=save)


    if not editor.validate():
        print('Editor form is not valid')
        return render_template('add_form.html', preview=custom_form, editor=editor, save=save)

    if editor.add_field.data:
        print('Field added (not really)')
        editor.field_name.data = ''

        field_name = request.form['field_name']
        field_type = field_cls[FieldType(int(request.form['field_type']))]

        field = {
            field_name: field_type(field_name, validators=[DataRequired()])
        }

        custom_form = custom_factory(**field)

    if editor.remove_field.data:
        print('Field removed (not really)')
        editor.field_name.data = ''

    return render_template('add_form.html', preview=custom_form, editor=editor, save=save)
