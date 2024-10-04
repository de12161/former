import configparser

from flask import Flask, g
from flask_bootstrap import Bootstrap5

from flask_wtf import CSRFProtect
from wtforms.fields.choices import SelectField
from wtforms.fields.form import FormField
from wtforms.fields.simple import StringField, FileField, BooleanField
from wtforms.validators import InputRequired

from .forms import HTMLForm, ImageForm
from .routes import index_page, form_editor_page, field_editor_page
from .database import FormDB
from .utils import Fields

from secrets import token_urlsafe

config = configparser.ConfigParser()
config.read('config.ini')

dfs_url = config['DFS']['url']

db_name = config['Database']['name']
if not config['Database'].getboolean('initialized'):
    FormDB(db_name).initialize()

    config['Database']['initialized'] = 'true'
    with open('config.ini', 'w') as config_file:
        config.write(config_file)

app = Flask(__name__)

app.register_blueprint(index_page)
app.register_blueprint(form_editor_page)
app.register_blueprint(field_editor_page)

app.config.from_object('flask_config')
app.secret_key = token_urlsafe(16)  # delete later

bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)

fields = Fields(
    default_data={
        'class': SelectField,
        'kwargs': {
            'validators': [InputRequired()]
        }
    },
    Bool={
        'class': BooleanField,
        'kwargs': {}
    },
    Text={
        'class': StringField,
        'kwargs': {
            'validators': [InputRequired()]
        }
    },
    TextArea={
        'class': FormField,
        'kwargs': {
            'form_class': HTMLForm,
        }
    },
    File={
        'class': FormField,
        'kwargs': {
            'form_class': ImageForm,
        }
    }
)

predefined_fields = [
    (fields.type.Bool, 'Checkbox'),
    (fields.type.Text, 'Text Field'),
    (fields.type.TextArea, 'HTML Area'),
    (fields.type.File, 'Image Field')
]


@app.before_request
def load_globals():
    g.db = FormDB(db_name)
    g.dfs_url = dfs_url
    g.fields = fields
    g.predefined_fields = predefined_fields
