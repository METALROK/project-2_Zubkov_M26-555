from primitive_db.decorators import confirm_action, handle_db_errors
from primitive_db.utils import load_table_data

VALID_TYPES = {"int", "str", "bool"}
TYPE_MAP = {"int": int, "str": str, "bool": bool}


@handle_db_errors
def create_table(metadata: dict, table_name: str, columns: list) -> dict:
    """
    Создаёт таблицу.
    """
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    table_columns = {"ID": "int"}

    for column in columns:
        name, sep, col_type = column.partition(":")
        if not sep or not name or col_type not in VALID_TYPES or name in table_columns:
            raise ValueError(column)
        table_columns[name] = col_type

    metadata[table_name] = table_columns

    columns_str = ", ".join(f"{name}:{type_}" for name, type_ in table_columns.items())
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_str}')
    return metadata

@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: dict, table_name: str) -> dict:
    """
    Удаляет таблицу из метаданных.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata

def list_tables(metadata):
    """
    Выводит список всех таблиц.
    """
    if not metadata:
        print("Таблиц пока нет.")
        return

    for table_name in metadata:
        print(f"- {table_name}")

def convert_value(
        value: int | str | bool,
        column_type: int | str | bool
        ) -> int | str | bool:
    """
    Проверяет, что значение соответствует типу столбца.

    Иначе выбрасывает ValueError.
    """
    if type(value) is not TYPE_MAP[column_type]:
        raise ValueError(value)
    return value

def cast_clause(metadata: dict, table_name: str, clause: dict) -> dict:
    """
    Проверяет столбцы условия и приводит значения к их типам.
    """
    columns = metadata[table_name]
    result = {}
    for column, value in clause.items():
        if column not in columns:
            raise ValueError(column)
        result[column] = convert_value(value, columns[column])
    return result

def _matches(record: dict, where_clause: dict) -> bool:
    """
    Проверяет, подходит ли запись под все условия where.
    """
    return all(record.get(key) == value for key, value in where_clause.items())

@handle_db_errors
def insert(metadata: dict, table_name: str, values: list) -> list | None:
    """Добавляет запись. Возвращает обновлённые данные или None при ошибке."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    columns = metadata[table_name]
    data_columns = [name for name in columns if name != "ID"]

    if len(values) != len(data_columns):
        print(
            f"Ошибка: ожидается {len(data_columns)} значений, "
            f"получено {len(values)}."
        )
        return None

    record = {
        name: convert_value(value, columns[name])
        for name, value in zip(data_columns, values)
    }

    table_data = load_table_data(table_name)
    new_id = max((row["ID"] for row in table_data), default=0) + 1
    table_data.append({"ID": new_id, **record})

    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data

def select(table_data: list, where_clauses: dict=None) -> list:
    """
    Возвращает все записи или только подходящие под where_clause.
    """
    if not where_clauses:
        return table_data
    return [record for record in table_data if _matches(record, where_clauses)]

def update(table_data: list, set_clause: dict, where_clause: dict) -> list:
    """
    Обновляет поля из set_clause в записях, подходящих под where_clause.
    """
    for record in table_data:
        if _matches(record, where_clause):
            record.update(set_clause)
    return table_data

@confirm_action("удаление таблицы")
def delete(table_data: list, where_clause: dict) -> list:
    """
    Удаляет записи, подходящие под where_clause.
    """
    return [record for record in table_data if not _matches(record, where_clause)]
