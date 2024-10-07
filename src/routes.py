import requests.exceptions

from flask import Blueprint, request, flash, g, session, redirect, url_for, render_template, send_file, abort

from wtforms.fields.choices import SelectField
from wtforms.fields.simple import SubmitField

from io import BytesIO
from PIL import Image

from sqlite3 import IntegrityError

from .utils import get_editor_choices, generate_fields, flash_errors, send_template, health_check, img_to_bytes
from .forms import create_form, create_editor, SaveFormForm, SelectFieldEditor, SaveSelectField, AuthForm


index_page = Blueprint('index_page', 'index_page', template_folder='templates')
@index_page.get('/')
@index_page.get('/forms')
def index():
    editor_mode = bool(g.editor_access or session.get('authorized'))
    forms = {}

    for form_label, form_id in g.db.get_forms_data().items():
        forms[form_label] = form_id

    return render_template('index.html', forms=forms, editor_mode=editor_mode, editor_access=g.editor_access)


form_page = Blueprint('form_page', 'form_page', template_folder='templates')
@form_page.route('/forms/<int:form_id>', methods=['GET', 'POST'])
def show(form_id):
    form_label, form_fields = g.db.get_form_by_id(form_id)

    form_fields = generate_fields(form_fields, g.fields)
    form_fields['submit'] = SubmitField('Отправить')

    form = create_form(form_fields)

    if request.method == 'GET':
        if not health_check(g.dfs_url):
            flash('Не удалось подключиться к API')
        return render_template('form.html', form=form, form_label=form_label)

    if not form.validate_on_submit():
        flash_errors(form)
        return redirect(url_for('form_page.show', form_id=form_id))

    form_files = dict(request.files)
    form_data = dict(request.form)
    del form_data['csrf_token']
    del form_data['submit']

    data = {}

    it = list(form_data.items())
    it.extend(list(form_files.items()))

    for key, value in it:
        if '-' in key:
            var_name, var_type = tuple(key.split('-'))

            if not data.get(var_name):
                data[var_name] = {}

            data[var_name][var_type] = value
        else:
            data[key] = value

    files = {}

    i = 0
    for value in data.values():
        if type(value) is not dict:
            continue

        if value.get('__type') == 'image':
            img = Image.open(value['source'])
            img_format = img.format.lower()
            files[f'image{i}.{img_format}'] = (f'image{i}.{img_format}', img_to_bytes(img), f'image/{img_format}')
            value['source'] = f'image{i}.{img_format}'
            value['__height'] = img.height
            value['__width'] = img.width
            i += 1

    doc_form = g.db.get_doc_form(form_label)

    try:
        response = send_template(g.dfs_url, doc_form, data, files)
    except requests.exceptions.ConnectionError:
        flash('Не удалось подключиться к API')
        return redirect(url_for('form_page.show', form_id=form_id))

    if not response.ok:
        flash('Что-то пошло не так')
        return redirect(url_for('form_page.show', form_id=form_id))

    return send_file(BytesIO(response.content), as_attachment=True, download_name='document.docx')


form_editor_page = Blueprint('form_editor_page', 'form_editor_page', template_folder='templates')
@form_editor_page.route('/form-editor', methods=['GET', 'POST'])
def form_editor():
    if not (g.editor_access or session.get('authorized')):
        return abort(401)

    if 'custom_fields' in session:
        custom_fields = session['custom_fields']
    else:
        custom_fields = {'static_fields': {}, 'select_fields': {}}

    editor = create_editor(get_editor_choices(g.predefined_fields, g.db.get_select_labels()))
    save = SaveFormForm()
    preview = create_form(generate_fields(custom_fields, g.fields))

    if request.method == 'GET':
        return render_template('form_editor.html', preview=preview, editor=editor, save=save, editor_access=g.editor_access)

    if save.delete_form.data:
        if not save.validate():
            flash_errors(save)
            return redirect(url_for('form_editor_page.form_editor'))

        if g.db.delete_form(request.form['form_label']):
            flash('Форма удалена')
        return redirect(url_for('form_editor_page.form_editor'))

    if save.save_form.data:
        if not save.validate():
            flash_errors(save)
            return redirect(url_for('form_editor_page.form_editor'))

        if not save.doc_form.data:
            flash('Не приложен шаблон')
            return redirect(url_for('form_editor_page.form_editor'))

        file = request.files['doc_form']

        custom_fields['doc_form'] = file.read()

        file.close()

        try:
            g.db.save_form(request.form['form_label'], custom_fields)

            custom_fields = {'static_fields': {}, 'select_fields': {}}
            session['custom_fields'] = custom_fields
            save.form_label.data = ''
        except IntegrityError:
            flash(f'Форма {save.form_label.data} уже существует')
            return redirect(url_for('form_editor_page.form_editor'))

        flash('Форма сохранена')
        return redirect(url_for('form_editor_page.form_editor'))

    if not editor.validate():
        flash_errors(editor)
        return redirect(url_for('form_editor_page.form_editor'))

    if editor.add_field.data:
        if request.form['field_type'].isdigit():
            field_name = request.form['field_name']
            field_type = request.form['field_type']
            field_label = request.form['field_label']

            if len(field_name) == 0:
                flash('Неверный идентификатор поля')
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
                flash('Неверный идентификатор поля')
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
    if not (g.editor_access or session.get('authorized')):
        return abort(401)

    if 'choices' in session:
        choices = session['choices']
    else:
        choices = []

    preview = create_form({'select': SelectField('', choices=choices)})
    editor = SelectFieldEditor()
    save = SaveSelectField()

    if request.method == 'GET':
        return render_template('field_editor.html', preview=preview, editor=editor, save=save, editor_access=g.editor_access)

    if save.delete_field.data:
        if not save.validate():
            flash_errors(save)
            return redirect(url_for('field_editor_page.field_editor'))

        field_label = request.form['field_label']

        editor_fields = session.get('custom_fields')
        if editor_fields:
            for field in editor_fields['select_fields'].values():
                if field_label == field['label']:
                    flash('Это поле используется в редакторе форм')
                    return redirect(url_for('field_editor_page.field_editor'))

        try:
            if g.db.delete_select_field(field_label):
                flash('Поле выбора удалено')
        except IntegrityError:
            flash('Нельзя удалить поле, так как оно используется как минимум одной формой')
            return redirect(url_for('field_editor_page.field_editor'))

        return redirect(url_for('field_editor_page.field_editor'))

    if save.save_field.data:
        if not save.validate():
            flash_errors(save)
            return redirect(url_for('field_editor_page.field_editor'))

        if len(choices) < 2:
            flash('Слишком мало опций для поля выбора')
            return redirect(url_for('field_editor_page.field_editor'))

        try:
            g.db.save_select_field(request.form['field_label'], choices)

            choices = []
            session['choices'] = choices
            save.field_label.data = ''
        except IntegrityError:
            flash(f'Поле {save.field_label.data} уже существует')
            return redirect(url_for('field_editor_page.field_editor'))

        flash('Поле сохранено')
        return redirect(url_for('field_editor_page.field_editor'))

    if not editor.validate():
        flash_errors(editor)
        return redirect(url_for('field_editor_page.field_editor'))

    if editor.add_choice.data:
        editor.choice_name.data = ''

        choice_name = request.form['choice_name']

        if choice_name not in choices:
            choices.append(choice_name)
            flash('Опция добавлена')

    if editor.remove_choice.data:
        editor.choice_name.data = ''

        choice_name = request.form['choice_name']

        if choice_name in choices:
            del choices[choices.index(choice_name)]
            flash('Опция убрана')

    session['choices'] = choices

    return redirect(url_for('field_editor_page.field_editor'))


auth_page = Blueprint('auth_page', 'auth_page', template_folder='templates')
@auth_page.route('/auth', methods=['GET', 'POST'])
def auth():
    if g.editor_access:
        return abort(503)

    auth_form = AuthForm()

    if request.method == 'GET':
        return render_template('auth.html', auth_form=auth_form)

    if not auth_form.validate_on_submit():
        flash_errors(auth_form)
        return redirect(url_for('auth_page.auth'))

    username = request.form['username']
    password = request.form['password']

    if len(password) < 8:
        flash('Пароль должен содержать хотя бы 8 символов')
        return redirect(url_for('auth_page.auth'))

    if password != request.form['repeat_pass']:
        flash('Пароли не совпадают')
        return redirect(url_for('auth_page.auth'))

    if auth_form.send_rq.data:
        if not g.editor_requests:
            flash('Запросы доступа на данный момент не принимаются')
            return redirect(url_for('auth_page.auth'))

        if not g.editors.register(username, password):
            flash('Запрос с таким именем уже был отправлен')
            return redirect(url_for('auth_page.auth'))

        flash('Запрос отправлен')
        return redirect(url_for('auth_page.auth'))

    if auth_form.authorize.data:
        if g.editors.authenticate(username, password):
            if g.editors.is_approved(username):
                session['authorized'] = True
                return redirect(url_for('index_page.index'))

            flash('Ваш запрос пока что не был одобрен')
            return redirect(url_for('auth_page.auth'))

        flash('Неверное имя или пароль')
        return redirect(url_for('auth_page.auth'))

    return redirect(url_for('auth_page.auth'))


@auth_page.route('/unauth')
def unauth():
    session['authorized'] = False
    return redirect(url_for('index_page.index'))
