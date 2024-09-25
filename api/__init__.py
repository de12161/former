from flask import Flask, render_template, url_for, request
from flask_bootstrap import Bootstrap5

from flask_wtf import CSRFProtect
from werkzeug.utils import redirect

from .forms import TestForm, AddFormForm, CustomForm

from secrets import token_urlsafe

key = token_urlsafe(16)

app = Flask(__name__)
app.secret_key = key

bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)

form_list = []


@app.get('/')
def index_get():
    return render_template('index.html', forms=form_list)


@app.post('/')
def index_post():
    print('POST request received:')
    for k, v in request.form.items():
        print(f'{k} = {v}')
    return 'Request successful'


@app.route('/add-form', methods=['GET', 'POST'])
def add_form():
    form = AddFormForm()
    if form.validate_on_submit():
        form.fields.data = ''
        new_form = CustomForm()
        fields = request.form['fields'].split('\n')
        for label in fields:
            new_form.fields.append_entry().label = label
        form_list.append(new_form)
    return render_template('add_form.html', form=form)
