from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap5

from flask_wtf import CSRFProtect

from .forms import TestForm, AddFormForm, CustomForm, StrVarEntryForm

from secrets import token_urlsafe

key = token_urlsafe(16)

app = Flask(__name__)
app.secret_key = key

bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)

form_list = {}


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
    form = AddFormForm()
    if form.is_submitted():
        print(f'Request: {request.form}')
    if form.validate_on_submit():
        print('Request validated')
        form.form_name.data = ''
        form.form_fields.data = ''

        new_form = CustomForm()

        labels = request.form['form_fields'].split('\n')
        for label in labels:
            new_form.text_fields.append_entry()
            new_form.text_fields[-1].label = label.strip()
            new_form.text_fields[-1].value.name = label.strip()

        form_list[request.form['form_name']] = new_form
    return render_template('add_form.html', form=form)
