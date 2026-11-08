VALID_TYPES = {"int", "str", "bool"}

def create_table(metadata: dict, table_name: str, columns: list) -> dict:
    """
    Создает таблицу.
    """
    if table_name in metadata:
        print(f"Ошибка: таблица '{table_name}' уже существует.")
        return metadata

    table_columns = {"ID": "int"}
    for column in columns:
        name, sep, col_type = column.partition(":")
        if not sep or not name or col_type not in VALID_TYPES or name in table_columns:
            print(f"Некорректное значение: {column}.")
            return metadata
        table_columns[name] = col_type

    metadata[table_name] = table_columns
    columns_str = ", ".join(f"{n}:{t}" for n, t in table_columns.items())
    print(f"Таблица '{table_name}' успешно создана со столбцами {columns_str}")
    return metadata

def drop_table(metadata: dict, table_name: str) -> dict:
    """
    Удаляет таблицу из метаданных.
    """
    if table_name not in metadata:
        print(f"Ошибка: таблица '{table_name}' не существует.")
        return metadata

    del metadata[table_name]
    print(f"Таблица '{table_name}' успешно удалена.")
    return metadata
