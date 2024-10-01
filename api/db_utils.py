import sqlite3


class FormDB:
    def __init__(self, db):
        self._con = sqlite3.connect(db, autocommit=True)

    def _get_choices(self, select_label):
        choices = []

        cur = self._con.cursor()

        rows = cur.execute(
            '''
            SELECT
            name_choice
            FROM
            select_field JOIN choice ON select_field.id_select = choice.id_select
            WHERE
            label_select = ?
            ''',
            (select_label,)
        ).fetchall()

        cur.close()

        for row in rows:
            choice = row[0]

            choices.append(choice)

        return choices

    def _get_select_fields(self, form_label):
        fields = {}

        cur = self._con.cursor()

        rows = cur.execute(
            '''
            SELECT
            label_select
            FROM
            form
            JOIN form_select ON form.id_form = form_select.id_form
            JOIN select_field ON form_select.id_select = select_field.id_select
            WHERE
            label_form = ?
            ''',
            (form_label,)
        ).fetchall()

        cur.close()

        for row in rows:
            select_label = row[0]
            choices = self._get_choices(select_label)

            fields[select_label] = choices

        return fields

    def _get_static_fields(self, form_label):
        fields = {}

        cur = self._con.cursor()

        rows = cur.execute(
            '''
            SELECT
            name_field, type_field, label_field
            FROM
            form JOIN field ON form.id_form = field.id_form WHERE label_form = ?
            ''',
            (form_label,)
        ).fetchall()

        cur.close()

        for row in rows:
            field_name = row[0]
            field_type = row[1]
            field_label = row[2]

            fields[field_name] = {
                'type': field_type,
                'label': field_label
            }

        return fields

    def _get_doc_form(self, form_label):
        cur = self._con.cursor()

        doc = cur.execute('SELECT doc_form FROM form WHERE label_form = ?', (form_label,)).fetchone()[0]

        cur.close()

        return doc

    def get_forms(self):
        forms = {}

        cur = self._con.cursor()

        rows = cur.execute('SELECT label_form FROM form').fetchall()

        cur.close()

        for row in rows:
            form_label = row[0]

            forms[form_label] = {
                'static_fields': self._get_static_fields(form_label),
                'select_fields': self._get_select_fields(form_label),
                'doc_form': self._get_doc_form(form_label)
            }

        return forms

    def save_select_field(self, select_label, choices):
        cur = self._con.cursor()

        cur.execute(
            'INSERT INTO select_field(label_select) VALUES (?)',
            (select_label,)
        )

        select_id = cur.execute(
            'SELECT id_select FROM select_field WHERE label_select = ?',
            (select_label,)
        ).fetchone()[0]

        choice_data = list(map(lambda choice: (select_id, choice), choices))
        cur.executemany('INSERT INTO choice(id_select, name_choice) VALUES (?, ?)', choice_data)

        cur.close()

    def _save_static_field(self, form_label, field_name, field_type, field_label):
        cur = self._con.cursor()

        form_id = cur.execute('SELECT id_form FROM form WHERE label_form=?', (form_label,)).fetchone()[0]

        cur.execute(
            'INSERT INTO field(id_form, name_field, type_field, label_field) VALUES (?, ?, ?, ?)',
            (form_id, field_name, field_type, field_label)
        )

        cur.close()

    def _link_form_select(self, form_label, select_label):
        cur = self._con.cursor()

        form_id = cur.execute(
            'SELECT id_form FROM form WHERE label_form = ?',
            (form_label,)
        ).fetchone()[0]

        select_id = cur.execute(
            'SELECT id_select FROM select_field WHERE label_select = ?',
            (select_label,)
        ).fetchone()[0]

        cur.execute('INSERT INTO form_select(id_form, id_select) VALUES (?, ?)', (form_id, select_id))

        cur.close()

    def save_form(self, form_label, doc_form, fields):
        cur = self._con.cursor()

        cur.execute('INSERT INTO form(label_form, doc_form) VALUES (?, ?)', (form_label, doc_form))

        if 'static_fields' in fields:
            for field_name, field_data in fields['static_fields'].items():
                self._save_static_field(form_label, field_name, field_data['type'], field_data['label'])

        if 'select_fields' in fields:
            for select_label in fields['select_fields']:
                self._link_form_select(form_label, select_label)

        cur.close()


def init_db(db):
    with sqlite3.connect(db) as con:
        cur = con.cursor()

        cur.execute('DROP TABLE IF EXISTS form')
        cur.execute('DROP TABLE IF EXISTS select_field')
        cur.execute('DROP TABLE IF EXISTS field')
        cur.execute('DROP TABLE IF EXISTS choice')
        cur.execute('DROP TABLE IF EXISTS form_select')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS form (
        id_form INTEGER PRIMARY KEY AUTOINCREMENT,
        label_form TEXT UNIQUE NOT NULL,
        doc_form BLOB NOT NULL
        )
        ''')
        cur.execute('''
        CREATE TABLE IF NOT EXISTS select_field (
        id_select INTEGER PRIMARY KEY AUTOINCREMENT,
        label_select TEXT UNIQUE NOT NULL
        )
        ''')
        cur.execute('''
        CREATE TABLE IF NOT EXISTS field (
        id_field INTEGER PRIMARY KEY AUTOINCREMENT,
        id_form INTEGER REFERENCES form(id_form) ON DELETE CASCADE NOT NULL,
        name_field TEXT NOT NULL,
        type_field INTEGER NOT NULL,
        label_field TEXT NOT NULL
        )
        ''')
        cur.execute('''
        CREATE TABLE IF NOT EXISTS choice (
        id_choice INTEGER PRIMARY KEY AUTOINCREMENT,
        id_select INTEGER REFERENCES select_field(id_select) ON DELETE CASCADE NOT NULL,
        name_choice TEXT NOT NULL
        )
        ''')
        cur.execute('''
        CREATE TABLE IF NOT EXISTS form_select (
        id_fs INTEGER PRIMARY KEY AUTOINCREMENT,
        id_form INTEGER REFERENCES form(id_form) ON DELETE CASCADE NOT NULL,
        id_select INTEGER REFERENCES select_field(id_select) ON DELETE RESTRICT NOT NULL
        )
        ''')


def main():
    db = input('Choose a location for the database: ')

    print(f'Initializing {db}...')
    init_db(db)
    print('Database initialized')


if __name__ == '__main__':
    main()
