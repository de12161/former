import sqlite3
from functools import wraps


class FormDB:
    def __init__(self, db):
        self.__con = sqlite3.connect(db)

    def __del__(self):
        self.__con.commit()
        self.__con.close()

    def __create_cursor(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            cur = self.__con.cursor()
            ret = func(self, cur, *args, **kwargs)
            cur.close()
            return ret
        return wrapper

    @__create_cursor
    def get_forms(self, _cur):
        forms = {}

        rows = _cur.execute('''
        SELECT
        name_form, doc_form, name_field, type_field, label_field, name_choice
        FROM
        form LEFT JOIN field ON form.id_form = field.id_form LEFT JOIN choice ON field.id_field = choice.id_field
        ''').fetchall()

        for row in rows:
            form = row[0]
            doc = row[1]
            field = row[2]
            field_type = row[3]
            field_label = row[4]
            choice = row[5]

            if forms.get(form) is None:
                forms[form] = {}

            forms[form]['doc_form'] = doc

            if field is None:
                continue

            if forms[form].get('fields') is None:
                forms[form]['fields'] = {}

            if forms[form]['fields'].get(field) is None:
                forms[form]['fields'][field] = {}

            forms[form]['fields'][field]['type'] = field_type
            forms[form]['fields'][field]['label'] = field_label

            if choice is None:
                continue

            if forms[form]['fields'][field].get('choices') is None:
                forms[form]['fields'][field]['choices'] = []

            forms[form]['fields'][field]['choices'].append(choice)

        return forms

    @__create_cursor
    def save_form(self, _cur, form_name, fields, doc_form):
        _cur.execute('INSERT INTO form(name_form, doc_form) VALUES (?, ?)', (form_name, doc_form))

        if len(fields.items()) == 0:
            return

        form_id = _cur.execute('SELECT id_form FROM form WHERE name_form=?', (form_name,)).fetchone()[0]

        for field_name, field_data in fields.items():
            _cur.execute(
                'INSERT INTO field(id_form, name_field, type_field, label_field) VALUES (?, ?, ?, ?)',
                (form_id, field_name, field_data['type'], field_data['label'])
            )

            if field_data.get('choices') is None:
                continue

            field_id = _cur.execute('SELECT id_field FROM field WHERE name_field=?', (field_name,)).fetchone()[0]

            for choice in field_data['choices']:
                _cur.execute('INSERT INTO choice(id_field, name_choice) VALUES (?, ?)', (field_id, choice))


def init_db(db):
    with sqlite3.connect(db) as con:
        cur = con.cursor()

        cur.execute('DROP TABLE IF EXISTS form')
        cur.execute('DROP TABLE IF EXISTS field')
        cur.execute('DROP TABLE IF EXISTS choice')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS form (
        id_form INTEGER PRIMARY KEY AUTOINCREMENT,
        name_form TEXT UNIQUE NOT NULL,
        doc_form BLOB NOT NULL
        )
        ''')
        cur.execute('''
        CREATE TABLE IF NOT EXISTS field (
        id_field INTEGER PRIMARY KEY AUTOINCREMENT,
        id_form INTEGER REFERENCES form(id_form) ON DELETE CASCADE NOT NULL,
        name_field TEXT UNIQUE NOT NULL,
        type_field INTEGER NOT NULL,
        label_field TEXT NOT NULL
        )
        ''')
        cur.execute('''
        CREATE TABLE IF NOT EXISTS choice (
        id_choice INTEGER PRIMARY KEY AUTOINCREMENT,
        id_field INTEGER REFERENCES field(id_field) ON DELETE CASCADE NOT NULL,
        name_choice TEXT NOT NULL
        )
        ''')


def main():
    db = input('Choose a location for the database: ')

    print(f'Initializing {db}...')
    init_db(db)
    print('Database initialized')


if __name__ == '__main__':
    main()
