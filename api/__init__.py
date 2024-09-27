from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap5

from flask_wtf import CSRFProtect
from wtforms.fields.simple import StringField, FileField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

from .forms import CustomFormFactory, AddFormFormFactory

from secrets import token_urlsafe

key = token_urlsafe(16)

app = Flask(__name__)
app.secret_key = key

bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)

custom_factory = CustomFormFactory({'text': StringField, 'img': FileField, 'html': TextAreaField})
add_form_factory = AddFormFormFactory(*custom_factory.field_types.keys())

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
    form = add_form_factory()
    if form.is_submitted():
        print(f'Request: {request.form}')
    if form.validate_on_submit():
        print('Request validated')
        form.form_name.data = ''
        form.form_fields.data = ''

        form_fields = {}
        request_fields = request.form['form_fields'].split('\n')
        for field in request_fields:
            field_name, field_type  = tuple(map(str.strip, field.split(':')))
            form_fields[field_name] = {'type': field_type, 'kwargs': {
                'label': field_name,
                'id': f'{field_name}-{str(len(form_list))}',
                'validators': [DataRequired()]
            }}

        new_form = custom_factory(**form_fields)

        form_list[request.form['form_name']] = new_form
    return render_template('add_form.html', form=form)
