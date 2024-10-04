import requests
import json

from enum import IntEnum

from flask import flash


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
        choices['Pre-defined fields'] = predefined

    if len(select) > 0:
        choices['Custom select fields'] = select

    return choices


def generate_fields(field_dict, field_classes):
    fields = {}

    for field_name, field_data in field_dict['static_fields'].items():
        field_class_data = field_classes[int(field_data['type'])]
        fields[field_name] = field_class_data['class'](field_data['label'] or field_name, validators=field_class_data['validators'])

    for field_name, field_data in field_dict['select_fields'].items():
        field_class_data = field_classes['default']
        fields[field_name] = field_class_data['class'](
            field_data['label'],
            validators=field_class_data['validators'],
            choices=field_data['choices']
        )

    return fields


def health_check(url):
    url += 'api/health-check'

    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        return False

    return r.ok


def send_template(url, doc_form, data):
    url += 'api/generate-document'

    payload = {
        'data': json.dumps(data)
    }

    files = {
        'doc_form': ('template.docx', doc_form, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    }

    r = requests.post(url, files=files, data=payload)

    return r
