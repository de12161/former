from sqlite3 import IntegrityError

from flask import Flask, render_template, request, session, url_for, redirect, flash
from flask_bootstrap import Bootstrap5

from flask_wtf import CSRFProtect
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, FileField, TextAreaField, BooleanField, SubmitField, HiddenField
from wtforms.validators import InputRequired

from .forms import create_form, create_editor, SaveFormForm, SelectFieldEditor, SaveSelectField
from .utils import get_editor_choices, generate_fields, flash_errors, send_template, get_config_data, health_check
from .db_utils import FormDB

from enum import IntEnum, auto

from secrets import token_urlsafe

key = token_urlsafe(16)

app = Flask(__name__)
app.secret_key = key

bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)

db_name = 'forms.db'
config = get_config_data('config.txt')


class FieldType(IntEnum):
    Bool = auto()
    Text = auto()
    TextArea = auto()
    File = auto()


field_class = {
    FieldType.Bool.value: {
        'class': BooleanField,
        'validators': []
    },
    FieldType.Text.value: {
        'class': StringField,
        'validators': [InputRequired()]
    },
    FieldType.TextArea.value: {
        'class': TextAreaField,
        'validators': [InputRequired()]
    },
    FieldType.File.value: {
        'class': FileField,
        'validators': [InputRequired()]
    },
    'select': {
        'class': SelectField,
        'validators': [InputRequired()]
    }
}

predefined_fields = [
    (FieldType.Bool.value, 'Checkbox'),
    (FieldType.Text.value, 'Text Field'),
    (FieldType.TextArea.value, 'Text Area'),
    (FieldType.File.value, 'File Field')
]


@app.get('/')
def index():
    db = FormDB(db_name)

    form = {}
    for form_label, field_data in db.get_forms().items():
        fields = generate_fields(field_data, field_class)
        fields['submit'] = SubmitField('Submit')
        fields['form_label'] = HiddenField(default=form_label)
        form[form_label] = create_form(fields)

    return render_template('index.html', forms=form)


@app.post('/')
def index_post():
    db = FormDB(db_name)

    doc_form = db.get_doc_form(request.form['form_label'])

    data = dict(request.form)
    del data['form_label']
    del data['csrf_token']
    del data['submit']

    print('Connecting to API...')

    connection = health_check(config['url'])

    if not connection:
        print('Couldn\'t connect to API')
        flash('Couldn\'t connect to API')
        return redirect(url_for('index'))

    print(f'Sending request...')

    response = send_template(config['url'], doc_form, data)

    print(f'Response text: {response.text}')

    return 'Request sent'


@app.route('/add-form', methods=['GET', 'POST'])
def add_form():
    if 'custom_fields' in session:
        custom_fields = session['custom_fields']
    else:
        custom_fields = {'static_fields': {}, 'select_fields': {}}

    db = FormDB(db_name)

    editor = create_editor(get_editor_choices(predefined_fields, db.get_select_labels()))
    save = SaveFormForm()
    preview = create_form(generate_fields(custom_fields, field_class))

    if request.method == 'GET':
        return render_template('add_form.html', preview=preview, editor=editor, save=save)

    if save.delete_form.data and save.validate():
        db.delete_form(request.form['form_label'])
        return redirect(url_for('add_form'))

    if save.save_form.data and save.validate():
        file = request.files['doc_form']

        custom_fields['doc_form'] = file.read()

        file.close()

        try:
            db.save_form(request.form['form_label'], custom_fields)

            custom_fields = {'static_fields': {}, 'select_fields': {}}
            session['custom_fields'] = custom_fields
            save.form_label.data = ''
        except IntegrityError:
            flash(f'Form {save.form_label.data} already exists')

        return redirect(url_for('add_form'))

    flash_errors(save)

    if not editor.validate():
        flash_errors(editor)
        return redirect(url_for('add_form'))

    if editor.add_field.data:
        if len(request.form['field_type']) < 5:
            field_name = request.form['field_name']
            field_type = request.form['field_type']
            field_label = request.form['field_label']

            if len(field_name) == 0 or len(field_label) == 0:
                flash('Invalid name or label')
                return redirect(url_for('add_form'))

            if field_name in custom_fields['select_fields']:
                del custom_fields['select_fields'][field_name]

            custom_fields['static_fields'][field_name] = {
                'type': field_type,
                'label': field_label
            }
        else:
            field_name = request.form['field_name']
            field_label = request.form['field_type']

            if len(field_name) == 0:
                flash('Invalid name')
                return redirect(url_for('add_form'))

            if field_name in custom_fields['static_fields']:
                del custom_fields['static_fields'][field_name]

            custom_fields['select_fields'][field_name] = {
                'choices': db.get_choices(field_label),
                'label': field_label
            }

        editor.field_name.data = ''

    if editor.remove_field.data:
        field_name = request.form['field_name']

        if field_name in custom_fields['static_fields']:
            del custom_fields['static_fields'][field_name]

        if field_name in custom_fields['select_fields']:
            del custom_fields['select_fields'][field_name]

        editor.field_name.data = ''

    session['custom_fields'] = custom_fields

    return redirect(url_for('add_form'))


@app.route('/add_field', methods=['GET', 'POST'])
def add_field():
    if 'choices' in session:
        choices = session['choices']
    else:
        choices = []

    db = FormDB(db_name)

    preview = create_form({'select': SelectField('', choices=choices)})
    editor = SelectFieldEditor()
    save = SaveSelectField()

    if request.method == 'GET':
        return render_template('add_field.html', preview=preview, editor=editor, save=save)

    if save.delete_field.data and save.validate():
        try:
            db.delete_select_field(request.form['field_label'])
        except IntegrityError:
            flash('Cannot delete field as it is used by at least one form')
        return redirect(url_for('add_field'))

    if save.save_field.data and save.validate():
        try:
            db.save_select_field(request.form['field_label'], choices)

            choices = []
            session['choices'] = choices
            save.field_label.data = ''
        except IntegrityError:
            flash(f'Field {save.field_label.data} already exists')

        return redirect(url_for('add_field'))

    flash_errors(save)

    if not editor.validate():
        flash_errors(editor)
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
