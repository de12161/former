import configparser
import os

from flask import Flask, g

from flask_wtf import CSRFProtect
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, BooleanField, TextAreaField
from wtforms.validators import InputRequired

from .routes import index_page, form_page, form_editor_page, field_editor_page
from .database import FormDB
from .utils import Fields

from dotenv import load_dotenv

load_dotenv('.flaskenv')
load_dotenv()

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

app.secret_key = os.environ.get('SECRET_KEY')

app.register_blueprint(index_page)
app.register_blueprint(form_page)
app.register_blueprint(form_editor_page)
app.register_blueprint(field_editor_page)

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
    },
    Text={
        'class': StringField,
        'kwargs': {
            'validators': [InputRequired()]
        }
    },
    TextArea={
        'class': TextAreaField,
        'kwargs': {
            'validators': [InputRequired()],
        },
        'type': 'html'
    },
    File={
        'class': FileField,
        'kwargs': {
            'validators': [FileRequired(), FileAllowed(['png', 'jpg'])]
        },
        'type': 'image'
    }
)

predefined_fields = [
    (fields.type.Bool, 'Флажок'),
    (fields.type.Text, 'Текстовое поле'),
    (fields.type.TextArea, 'Поле для HTML'),
    (fields.type.File, 'Картинка')
]


@app.before_request
def load_globals():
    g.db = FormDB(db_name)
    g.dfs_url = dfs_url
    g.fields = fields
    g.predefined_fields = predefined_fields
