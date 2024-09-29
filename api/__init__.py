from flask import Flask, render_template, request, session, url_for, redirect
from flask_bootstrap import Bootstrap5

from flask_wtf import CSRFProtect
from wtforms.fields.simple import StringField, FileField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired

from .forms import create_form, create_editor, SaveFormForm
from enum import IntEnum, auto

from secrets import token_urlsafe

key = token_urlsafe(16)

app = Flask(__name__)
app.secret_key = key

bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)


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

choice_list = {
    'Pre-defined fields': [
        (FieldType.Bool.value, 'Checkbox'),
        (FieldType.Text.value, 'Text Field'),
        (FieldType.TextArea.value, 'Text Area'),
        (FieldType.File.value, 'File Field')
    ],

    'Custom select fields': []
}


def to_fields(fields):
    field_dict = {}

    for field_name, field_type in fields.items():
        field_class = field_cls[FieldType(int(field_type))]
        field_dict[field_name] = field_class(field_name, validators=[DataRequired()])

    return field_dict


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
    if 'custom_fields' in session:
        custom_fields = session['custom_fields']
    else:
        custom_fields = {}

    editor = create_editor(choice_list)
    save_form = SaveFormForm()
    custom_form = create_form(to_fields(custom_fields))

    if request.method == 'GET':
        return render_template('add_form.html', preview=custom_form, editor=editor, save=save_form)


    if save_form.submit.data and save_form.validate():
        print('Form saved (actually saved)')
        save_form.form_name.data = ''

        custom_fields = to_fields(custom_fields)
        custom_fields['submit'] = SubmitField('Submit')

        form_name = request.form['form_name']
        form_list[form_name] = create_form(custom_fields)

        custom_fields = {}
        session['custom_fields'] = custom_fields

        return redirect(url_for('add_form'))


    if not editor.validate():
        return redirect(url_for('add_form'))

    if editor.add_field.data:
        editor.field_name.data = ''

        field_name = request.form['field_name']
        field_type = request.form['field_type']

        custom_fields[field_name] = field_type

    if editor.remove_field.data:
        editor.field_name.data = ''

        field_name = request.form['field_name']
        del custom_fields[field_name]

    session['custom_fields'] = custom_fields

    return redirect(url_for('add_form'))
