from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap5

from flask_wtf import CSRFProtect

from .forms import TestForm

from secrets import token_urlsafe

key = token_urlsafe(16)

app = Flask(__name__)
app.secret_key = key

bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)


@app.get('/')
def index_get():
    form = TestForm()
    return render_template('index.html', form=form)


@app.post('/')
def index_post():
    return 'Request successful'


@app.route('/add-form')
def add_form():
    return render_template('add_form.html')
