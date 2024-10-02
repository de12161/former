def get_editor_choices(predefined, select):
    select_names = select

    choices = {}

    if len(predefined) > 0:
        choices['Pre-defined fields'] = predefined

    if len(select_names) > 0:
        choices['Custom select fields'] = select_names

    return choices


def to_fields(field_dict, field_classes):
    fields = {}

    for field_name, field_data in field_dict['static_fields'].items():
        field_class_data = field_classes[int(field_data['type'])]
        fields[field_name] = field_class_data['class'](field_data['label'], validators=field_class_data['validators'])

    for field_name, field_data in field_dict['select_fields'].items():
        field_class_data = field_classes['select']
        fields[field_name] = field_class_data['class'](
            field_data['label'],
            validators=field_class_data['validators'],
            choices=field_data['choices']
        )

    return fields
