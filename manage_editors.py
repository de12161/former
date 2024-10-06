from src.database import EditorDB
from src import editor_db


def search_data(db):
    name = input('Введите имя: ')

    if editor := db.search(name):
        return to_str(editor)

    return f'Имя {name} не найдено'


def approve(db):
    name = input('Введите имя: ')

    if db.approve(name):
        return 'Запрос одобрен'

    return f'Имя {name} не найдено'


def get_by_approval(db, approval):
    rows = db.get_by_approval(approval)

    if not rows:
        return 'Пусто'

    rows_str = []
    for row in rows:
        rows_str.append(to_str(row))

    return '\n'.join(rows_str)


def delete_data(db):
    name = input('Введите имя: ')

    if db.delete(name):
        return 'Информация удалена'

    return f'Имя {name} не найдено'


def to_str(row):
    items = []

    row_str = [str(item) for item in row]

    length = len(max(row_str, key=len))

    for item in row_str:
        items.append(f'{item:{length}}')

    return ' | '.join(items)


def main():
    db = EditorDB(editor_db)

    while True:
        cmd = input(
'''Выберите действие:
0 - Выход
1 - Просмотреть список редакторов
2 - Просмотреть список одобренных запросов
3 - Просмотреть список неодобренных запросов
4 - Поиск редактора по имени
5 - Одобрить запрос
6 - Удалить информацию о редакторе
'''
        )

        if cmd == '0':
            break
        elif cmd == '1':
            rows = []

            rows.extend(db.get_by_approval(False))
            rows.extend(db.get_by_approval(True))

            print('-' * 20)
            for row in rows:
                print(to_str(row))
            print('-' * 20)
        elif cmd == '2':
            print('-' * 20)
            print(get_by_approval(db, True))
            print('-' * 20)
        elif cmd == '3':
            print('-' * 20)
            print(get_by_approval(db, False))
            print('-' * 20)
        elif cmd == '4':
            print('-' * 20)
            print(search_data(db))
            print('-' * 20)
        elif cmd == '5':
            print('-' * 20)
            print(approve(db))
            print('-' * 20)
        elif cmd == '6':
            print('-' * 20)
            print(delete_data(db))
            print('-' * 20)


if __name__ == '__main__':
    main()
