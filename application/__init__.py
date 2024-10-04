import configparser

from flask import Flask, g
from flask_bootstrap import Bootstrap5

from flask_wtf import CSRFProtect
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, FileField, TextAreaField, BooleanField
from wtforms.validators import InputRequired

from .database import FormDB
from .routes import index_page, form_editor_page, field_editor_page

from enum import IntEnum, auto

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
        'validators': [InputRequired()]
    },
    FieldType.TextArea.value: {
        'class': TextAreaField,
        'validators': [InputRequired()]
    },
    FieldType.File.value: {
        'class': FileField,
        'validators': [InputRequired()]
    },
    'select': {
        'class': SelectField,
        'validators': [InputRequired()]
    }
}

predefined_fields = [
    (FieldType.Bool.value, 'Checkbox'),
    (FieldType.Text.value, 'Text Field'),
    (FieldType.TextArea.value, 'Text Area'),
    (FieldType.File.value, 'File Field')
]


@app.before_request
def load_globals():
    g.db = FormDB(db_name)
    g.dfs_url = dfs_url
    g.field_class = field_class
    g.predefined_fields = predefined_fields
