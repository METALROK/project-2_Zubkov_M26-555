import shlex

import prompt

from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata

META_FILE = "db_meta.json"
COMMANDS = {"create_table", "drop_table", "list_tables", "help", "exit"}


def print_help():
    """
    Выводит справочную информацию.
    """
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table имя_таблицы столбец1:тип столбец2:тип .. "
          "- создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table имя_таблицы - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def run():
    """
    Главный цикл.
    """
    print_help()

    while True:
        metadata = load_metadata(META_FILE)
        user_input = prompt.string(">>>Введите команду: ")

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}.")
            continue

        if not args:
            continue

        match args:
            case ["exit"]:
                return
            case ["help"]:
                print_help()
            case ["list_tables"]:
                list_tables(metadata)
            case ["create_table", table_name, *columns]:
                metadata = create_table(metadata, table_name, columns)
                save_metadata(META_FILE, metadata)
            case ["drop_table", table_name]:
                metadata = drop_table(metadata, table_name)
                save_metadata(META_FILE, metadata)
            case [command, *_] if command in COMMANDS:
                print(f"Некорректное значение: {user_input}.")
            case [command, *_]:
                print(f"Функции {command} нет.")
