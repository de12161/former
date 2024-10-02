from flask import Flask, render_template, request, session, url_for, redirect
from flask_bootstrap import Bootstrap5

from flask_wtf import CSRFProtect
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, FileField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired

from .forms import create_form, create_editor, SaveFormForm, SelectFieldEditor, SaveSelectField
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

predefined_fields = [
    (FieldType.Bool.value, 'Checkbox'),
    (FieldType.Text.value, 'Text Field'),
    (FieldType.TextArea.value, 'Text Area'),
    (FieldType.File.value, 'File Field')
]


def get_select_fields():
    return []


def get_editor_choices(predefined=None):
    if predefined is None:
        predefined = []

    select_fields = get_select_fields()

    choices = {}

    if len(predefined) > 0:
        choices['Pre-defined fields'] = predefined

    if len(select_fields) > 0:
        choices['Custom select fields'] = select_fields

    return choices


def save_form(form_name, form_fields):
    form_list[form_name] = form_fields


def get_forms():
    ret = {}

    for form_name, fields_text in form_list.items():
        form_fields = to_fields(fields_text)
        form_fields['submit'] = SubmitField('Submit')
        ret[form_name] = create_form(form_fields)

    return ret


def to_fields(fields):
    field_dict = {}

    for field_name, field_type in fields.items():
        field_class = field_cls[FieldType(int(field_type))]
        vals = [] if field_class is BooleanField else [DataRequired()]
        field_dict[field_name] = field_class(field_name, validators=vals)

    return field_dict


@app.get('/')
def index_get():
    return render_template('index.html', forms=get_forms())


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

    editor = create_editor(get_editor_choices(predefined_fields))
    save = SaveFormForm()
    custom_form = create_form(to_fields(custom_fields))

    if request.method == 'GET':
        return render_template('add_form.html', preview=custom_form, editor=editor, save=save)


    if save.submit.data and save.validate():
        save.form_name.data = ''

        save_form(request.form['form_name'], custom_fields)

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


@app.route('/add_field', methods=['GET', 'POST'])
def add_field():
    if 'choices' in session:
        choices = session['choices']
    else:
        choices = []

    print(f'Request: {request.form}')
    print(f'Choices: {choices}')

    preview = create_form({'select': SelectField('', choices=choices)})
    editor = SelectFieldEditor()
    save = SaveSelectField()

    if request.method == 'GET':
        return render_template('add_field.html', preview=preview, editor=editor, save=save)


    if save.submit.data and save.validate():
        save.field_label.data = ''

        # save_form(request.form['form_name'], custom_fields)

        # custom_fields = {}
        # session['custom_fields'] = custom_fields

        return redirect(url_for('add_field'))


    if not editor.validate():
        return redirect(url_for('add_field'))

    if editor.add_choice.data:
        editor.choice_name.data = ''

        choice_name = request.form['choice_name']

        if choice_name not in choices:
            choices.append(choice_name)

    if editor.remove_choice.data:
        editor.choice_name.data = ''

        choice_name = request.form['choice_name']

        if choice_name in choices:
            del choices[choices.index(choice_name)]

    session['choices'] = choices

    return redirect(url_for('add_field'))
