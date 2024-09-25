from flask import Flask, render_template, url_for, request
from flask_bootstrap import Bootstrap5

from flask_wtf import CSRFProtect
from werkzeug.utils import redirect

from .forms import TestForm, AddFormForm

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
    return 'Request successful'


@app.get('/add-form')
def add_form():
    return render_template('add_form.html', form=AddFormForm())


@app.post('/add-form')
def add_form_post():
    form_list.append(TestForm())
    return redirect(url_for('add_form'))
