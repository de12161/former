import requests
import json

from enum import IntEnum

from io import BytesIO

from flask import flash
from wtforms.fields.simple import HiddenField


class Fields:
    def __init__(self, default_data, **kwargs):
        types = kwargs
        types['default'] = default_data
        enum_dict = dict((v, k) for k, v in enumerate(types.keys()))

        self._type = IntEnum('Type', enum_dict)
        self._cls = {}

        for ftype, data in types.items():
            self._cls[self._type[ftype]] = data

    @property
    def type(self):
        return self._type

    def __getitem__(self, item):
        if item in self.type:
            return self._cls[self._type(item)]

        return self._cls[self._type['default']]


def flash_errors(form):
    if form.errors:
        for error in form.errors.values():
            flash(error)


def get_editor_choices(predefined, select):
    choices = {}

    if len(predefined) > 0:
        choices['Предопределённые поля'] = predefined

    if len(select) > 0:
        choices['Пользовательские поля выбора'] = select

    return choices


def generate_fields(field_dict, field_classes):
    fields = {}

    for field_name, field_data in field_dict['static_fields'].items():
        field_class_data = field_classes[int(field_data['type'])]

        if 'type' in field_class_data:
            fields[f'{field_name}-source'] = field_class_data['class'](
                label=field_name,
                **field_class_data.get('kwargs', {})
            )
            fields[f'{field_name}-__type'] = HiddenField(label='', default=field_class_data['type'])
        else:
            fields[field_name] = field_class_data['class'](
                label=field_data['label'] or field_name,
                **field_class_data.get('kwargs', {})
            )

    for field_name, field_data in field_dict['select_fields'].items():
        field_class_data = field_classes['default']

        fields[field_name] = field_class_data['class'](
            label=field_data['label'],
            **field_class_data['kwargs'],
            choices=field_data['choices']
        )

    return fields


def img_to_bytes(img):
    b = BytesIO()

    img.save(b, format=img.format)

    return b.getvalue()


def health_check(url):
    url += '/api/health-check'

    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        return False

    return r.ok


def send_template(url, doc_form, data, files):
    url += '/api/generate-document'

    payload = {
        'data': json.dumps(data)
    }

    file_payload = files
    file_payload['doc_form'] = ('template.docx', doc_form, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')

    r = requests.post(url, files=file_payload, data=payload)

    return r
