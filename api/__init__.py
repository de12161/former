from flask import Flask, render_template
from flask_bootstrap import Bootstrap

from flask_wtf import CSRFProtect

from secrets import token_urlsafe

key = token_urlsafe(16)

app = Flask(__name__)
app.secret_key = key

bootstrap = Bootstrap(app)
csrf = CSRFProtect(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add-form')
def add_form():
    return render_template('add_form.html')
