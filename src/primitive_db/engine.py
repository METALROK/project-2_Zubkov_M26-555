import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.constants import ID_COLUMN, META_FILE
from primitive_db.core import (
    cast_clause,
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.decorators import create_cacher, handle_db_errors
from primitive_db.parser import (
    parse_delete,
    parse_insert,
    parse_select,
    parse_set,
    parse_update,
    parse_values,
    parse_where,
)
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

select_cache = create_cacher()


def print_help():
    """
    Выводит справку по всем командам.
    """
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table имя_таблицы столбец1:тип столбец2:тип ... "
          "- создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table имя_таблицы - удалить таблицу")

    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into имя_таблицы values "
        "(значение1, значение2, ...) - создать запись."
    )
    print(
        "<command> select from имя_таблицы where столбец = значение "
        "- прочитать записи по условию."
    )
    print("<command> select from имя_таблицы - прочитать все записи.")
    print(
        "<command> update имя_таблицы set столбец1 = новое_значение1 "
        "where столбец_условия = значение_условия - обновить запись."
    )
    print(
        "<command> delete from имя_таблицы where столбец = значение "
        "- удалить запись."
    )
    print("<command> info имя_таблицы - вывести информацию о таблице.")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def _table_exists(metadata: dict, table_name: str) -> bool:
    """
    Проверяет существование таблицы.
    """
    if table_name not in metadata:
        print(f'Ошибка: таблица "{table_name}" не существует.')
        return False
    return True

def print_rows(columns: list, rows: list):
    """
    Выводит записи таблицей prettytable.
    """
    if not rows:
        print("Записи не найдены.")
        return

    table = PrettyTable()
    table.field_names = list(columns)
    for row in rows:
        table.add_row([row.get(column) for column in columns])
    print(table)

@handle_db_errors
def handle_insert(metadata: dict, user_input: str):
    """
    Реализация insert.
    """
    table_name, values_text = parse_insert(user_input)
    table_data = insert(metadata, table_name, parse_values(values_text))
    if table_data is not None:
        save_table_data(table_name, table_data)
        select_cache.clear()

@handle_db_errors
def handle_select(metadata: dict, user_input: str):
    """
    Реализация select.
    """
    table_name, where_text = parse_select(user_input)
    if not _table_exists(metadata, table_name):
        return

    where = None
    if where_text:
        where = cast_clause(metadata, table_name, parse_where(where_text))

    cache_key = (table_name, tuple(sorted(where.items())) if where else None)
    rows = select_cache(cache_key, lambda: select(load_table_data(table_name), where))
    print_rows(metadata[table_name], rows)

@handle_db_errors
def handle_update(metadata: dict, user_input: str):
    """
    Реализация update.
    """
    table_name, set_text, where_text = parse_update(user_input)
    if not _table_exists(metadata, table_name):
        return

    set_clause = cast_clause(metadata, table_name, parse_set(set_text))
    if ID_COLUMN in set_clause:
        raise ValueError(ID_COLUMN)
    where = cast_clause(metadata, table_name, parse_where(where_text))

    table_data = load_table_data(table_name)
    matched_ids = [record[ID_COLUMN] for record in select(table_data, where)]
    if not matched_ids:
        print("Записи не найдены.")
        return

    table_data = update(table_data, set_clause, where)
    save_table_data(table_name, table_data)
    select_cache.clear()
    for record_id in matched_ids:
        print(f'Запись с ID={record_id} в таблице "{table_name}" успешно обновлена.')

@handle_db_errors
def handle_delete(metadata: dict, user_input: str):
    """
    Реализация delete.
    """
    table_name, where_text = parse_delete(user_input)
    if not _table_exists(metadata, table_name):
        return

    where = cast_clause(metadata, table_name, parse_where(where_text))

    table_data = load_table_data(table_name)
    matched_ids = [record[ID_COLUMN] for record in select(table_data, where)]
    if not matched_ids:
        print("Записи не найдены.")
        return

    table_data = delete(table_data, where)
    if table_data is None:
        return

    save_table_data(table_name, table_data)
    select_cache.clear()
    for record_id in matched_ids:
        print(f'Запись с ID={record_id} успешно удалена из таблицы "{table_name}".')

def handle_info(metadata: dict, table_name: str):
    """
    Реализация info.
    """
    if not _table_exists(metadata, table_name):
        return

    columns = ", ".join(
        f"{name}:{type_}" for name, type_ in metadata[table_name].items()
    )
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {columns}")
    print(f"Количество записей: {len(load_table_data(table_name))}")

@handle_db_errors
def handle_simple_command(metadata: dict, user_input: str):
    """
    Команды без кавычек и выражений.
    """
    try:
        args = shlex.split(user_input)
    except ValueError:
        raise ValueError(user_input) from None

    match args:
        case ["list_tables"]:
            list_tables(metadata)
        case ["create_table", table_name, *columns]:
            create_table(metadata, table_name, columns)
            save_metadata(META_FILE, metadata)
        case ["drop_table", table_name]:
            if not _table_exists(metadata, table_name):
                return
            if drop_table(metadata, table_name) is not None:
                save_metadata(META_FILE, metadata)
                delete_table_data(table_name)
                select_cache.clear()
        case ["info", table_name]:
            handle_info(metadata, table_name)
        case _:
            raise ValueError(user_input)

def run():
    """
    Главный цикл.
    """
    print_help()

    while True:
        metadata = load_metadata(META_FILE)
        user_input = prompt.string(">>>Введите команду: ").strip()
        if not user_input:
            continue

        command = user_input.split()[0].lower()

        match command:
            case "exit":
                return
            case "help":
                print_help()
            case "insert":
                handle_insert(metadata, user_input)
            case "select":
                handle_select(metadata, user_input)
            case "update":
                handle_update(metadata, user_input)
            case "delete":
                handle_delete(metadata, user_input)
            case "create_table" | "drop_table" | "list_tables" | "info":
                handle_simple_command(metadata, user_input)
            case _:
                print(f"Функции {command} нет.")
