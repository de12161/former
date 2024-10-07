from src.database import EditorDB
from src import editor_db


def search_data(db):
    name = input('Введите имя: ')

    if editor := db.search(name):
        return to_str(editor, len(max([str(item) for item in editor], key=len)))

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

    length = get_max_length(rows)

    rows_str = []
    for row in rows:
        rows_str.append(to_str(row, length))

    return '\n'.join(rows_str)


def delete_data(db):
    name = input('Введите имя: ')

    if db.delete(name):
        return 'Информация удалена'

    return f'Имя {name} не найдено'


def to_str(row, length):
    items = []

    for item in row:
        items.append(f'{item:{length}}')

    return ' | '.join(items)


def get_max_length(rows):
    length = -1

    for row in rows:
        str_row = [str(item) for item in row]
        if (rl := len(max(str_row, key=len))) > length:
            length = rl

    return length


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
7 - Удалить все неодобренные запросы
'''
        )

        if cmd == '0':
            break
        elif cmd == '1':
            rows = []

            rows.extend(db.get_by_approval(False))
            rows.extend(db.get_by_approval(True))

            length = get_max_length(list(rows))

            print('-' * 20)
            for row in rows:
                print(to_str(row, length))
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
        elif cmd == '7':
            print('-' * 20)
            db.delete_all_nonapproved()
            print('Список неодобренных запросов очищен')
            print('-' * 20)


if __name__ == '__main__':
    main()
