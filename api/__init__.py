from flask import Flask, render_template, request, session, url_for, redirect
from flask_bootstrap import Bootstrap5

from flask_wtf import CSRFProtect
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, FileField, TextAreaField, BooleanField, SubmitField, HiddenField
from wtforms.validators import DataRequired

from .forms import create_form, create_editor, SaveFormForm, SelectFieldEditor, SaveSelectField
from .utils import get_editor_choices, to_fields
from .db_utils import FormDB

from enum import IntEnum, auto

from secrets import token_urlsafe

key = token_urlsafe(16)

app = Flask(__name__)
app.secret_key = key

bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)

db_name = 'forms.db'


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
        'validators': [DataRequired()]
    },
    FieldType.TextArea.value: {
        'class': TextAreaField,
        'validators': [DataRequired()]
    },
    FieldType.File.value: {
        'class': FileField,
        'validators': [DataRequired()]
    },
    'select': {
        'class': SelectField,
        'validators': [DataRequired()]
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
        fields = to_fields(field_data, field_class)
        fields['submit'] = SubmitField('Submit')
        fields['doc_form'] = HiddenField(default=field_data['doc_form'])
        form[form_label] = create_form(fields)

    return render_template('index.html', forms=form)


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
        custom_fields = {'static_fields': {}, 'select_fields': {}}

    db = FormDB(db_name)

    select_fields = db.get_select_labels()

    editor = create_editor(get_editor_choices(predefined_fields, select_fields))
    save = SaveFormForm()
    custom_form = create_form(to_fields(custom_fields, field_class))

    if request.method == 'GET':
        return render_template('add_form.html', preview=custom_form, editor=editor, save=save)


    if save.submit.data and save.validate():
        save.form_name.data = ''

        custom_fields['doc_form'] = request.form['doc_form']

        db.save_form(request.form['form_name'], custom_fields)

        custom_fields = {'static_fields': {}, 'select_fields': {}}
        session['custom_fields'] = custom_fields

        return redirect(url_for('add_form'))


    if not editor.validate():
        return redirect(url_for('add_form'))

    if editor.add_field.data:
        editor.field_name.data = ''

        if request.form['field_type'].isdigit():
            field_name = request.form['field_name']
            field_type = request.form['field_type']
            field_label = request.form['field_label']

            custom_fields['static_fields'][field_name] = {
                'type': field_type,
                'label': field_label
            }
        else:
            field_name = request.form['field_name']
            field_label = request.form['field_type']

            custom_fields['select_fields'][field_name] = {
                'choices': db.get_choices(field_label),
                'label': field_label
            }

    if editor.remove_field.data:
        editor.field_name.data = ''

        field_name = request.form['field_name']

        if field_name in custom_fields['static_fields']:
            del custom_fields['static_fields'][field_name]

        if field_name in custom_fields['select_fields']:
            del custom_fields['select_fields'][field_name]

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


    if save.submit.data and save.validate():
        save.field_label.data = ''

        db.save_select_field(request.form['field_label'], choices)

        choices = []
        session['choices'] = choices

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
