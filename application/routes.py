from flask import Blueprint, request, flash, g, session, redirect, url_for, render_template, send_file

from wtforms.fields.choices import SelectField
from wtforms.fields.simple import SubmitField, HiddenField

from io import BytesIO

from sqlite3 import IntegrityError

from .utils import get_editor_choices, generate_fields, flash_errors, send_template, health_check
from .forms import create_form, create_editor, SaveFormForm, SelectFieldEditor, SaveSelectField


index_page = Blueprint('index_page', 'index_page', template_folder='templates')
@index_page.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        form = {}
        for form_label, field_data in g.db.get_forms().items():
            fields = generate_fields(field_data, g.fields)
            fields['submit'] = SubmitField('Submit')
            fields['form_label'] = HiddenField(default=form_label)
            form[form_label] = create_form(fields)

        return render_template('index.html', forms=form)

    doc_form = g.db.get_doc_form(request.form['form_label'])

    data = dict(request.form)
    del data['form_label']
    del data['csrf_token']
    del data['submit']

    connection = health_check(g.dfs_url)

    if not connection:
        flash('Couldn\'t connect to API')
        return redirect(url_for('index_page.index'))

    response = send_template(g.dfs_url, doc_form, data)

    return send_file(BytesIO(response.content), as_attachment=True, download_name='document.docx')


form_editor_page = Blueprint('form_editor_page', 'form_editor_page', template_folder='templates')
@form_editor_page.route('/form-editor', methods=['GET', 'POST'])
def form_editor():
    if 'custom_fields' in session:
        custom_fields = session['custom_fields']
    else:
        custom_fields = {'static_fields': {}, 'select_fields': {}}

    editor = create_editor(get_editor_choices(g.predefined_fields, g.db.get_select_labels()))
    save = SaveFormForm()
    preview = create_form(generate_fields(custom_fields, g.fields))

    if request.method == 'GET':
        return render_template('form_editor.html', preview=preview, editor=editor, save=save)

    if save.delete_form.data and save.validate():
        g.db.delete_form(request.form['form_label'])
        return redirect(url_for('form_editor_page.form_editor'))

    if save.save_form.data and save.validate():
        file = request.files['doc_form']

        custom_fields['doc_form'] = file.read()

        file.close()

        try:
            g.db.save_form(request.form['form_label'], custom_fields)

            custom_fields = {'static_fields': {}, 'select_fields': {}}
            session['custom_fields'] = custom_fields
            save.form_label.data = ''
        except IntegrityError:
            flash(f'Form {save.form_label.data} already exists')

        return redirect(url_for('form_editor_page.form_editor'))

    flash_errors(save)

    if not editor.validate():
        flash_errors(editor)
        return redirect(url_for('form_editor_page.form_editor'))

    if editor.add_field.data:
        if len(request.form['field_type']) < 5:
            field_name = request.form['field_name']
            field_type = request.form['field_type']
            field_label = request.form['field_label']

            if len(field_name) == 0 or len(field_label) == 0:
                flash('Invalid name or label')
                return redirect(url_for('form_editor_page.form_editor'))

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
                return redirect(url_for('form_editor_page.form_editor'))

            if field_name in custom_fields['static_fields']:
                del custom_fields['static_fields'][field_name]

            custom_fields['select_fields'][field_name] = {
                'choices': g.db.get_choices(field_label),
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

    return redirect(url_for('form_editor_page.form_editor'))


field_editor_page = Blueprint('field_editor_page', 'field_editor_page', template_folder='templates')
@field_editor_page.route('/field-editor', methods=['GET', 'POST'])
def field_editor():
    if 'choices' in session:
        choices = session['choices']
    else:
        choices = []

    preview = create_form({'select': SelectField('', choices=choices)})
    editor = SelectFieldEditor()
    save = SaveSelectField()

    if request.method == 'GET':
        return render_template('field_editor.html', preview=preview, editor=editor, save=save)

    if save.delete_field.data and save.validate():
        field_label = request.form['field_label']

        for field in session['custom_fields']['select_fields'].values():
            if field_label == field['label']:
                flash('This field is being used in the form editor')
                return redirect(url_for('field_editor_page.field_editor'))

        try:
            g.db.delete_select_field(field_label)
        except IntegrityError:
            flash('Cannot delete field as it is used by at least one form')

        return redirect(url_for('field_editor_page.field_editor'))

    if save.save_field.data and save.validate():
        try:
            g.db.save_select_field(request.form['field_label'], choices)

            choices = []
            session['choices'] = choices
            save.field_label.data = ''
        except IntegrityError:
            flash(f'Field {save.field_label.data} already exists')

        return redirect(url_for('field_editor_page.field_editor'))

    flash_errors(save)

    if not editor.validate():
        flash_errors(editor)
        return redirect(url_for('field_editor_page.field_editor'))

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

    return redirect(url_for('field_editor_page.field_editor'))
