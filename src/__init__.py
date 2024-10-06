import configparser
import os

from flask import Flask, g, render_template

from flask_wtf import CSRFProtect
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, BooleanField, TextAreaField
from wtforms.validators import InputRequired

from .routes import index_page, form_page, form_editor_page, field_editor_page, auth_page
from .database import FormDB, EditorDB
from .utils import Fields

from dotenv import load_dotenv

load_dotenv('.flaskenv')
load_dotenv()

config = configparser.ConfigParser()
config.read('config.ini')

dfs_url = config['DFS']['url']
editor_access = config.getboolean('Editor_access', 'enabled')
editor_requests = config.getboolean('Editor_access', 'allow_requests')

db_name = 'forms.db'
FormDB(db_name).initialize()

editor_db = 'editors.db'
EditorDB(editor_db).initialize()

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY')

app.register_blueprint(index_page)
app.register_blueprint(form_page)
app.register_blueprint(form_editor_page)
app.register_blueprint(field_editor_page)
app.register_blueprint(auth_page)

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
    g.editors = EditorDB(editor_db)
    g.dfs_url = dfs_url
    g.fields = fields
    g.predefined_fields = predefined_fields
    g.editor_access = editor_access
    g.editor_requests = editor_requests


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(503)
def service_not_available(e):
    return render_template('503.html'), 503
