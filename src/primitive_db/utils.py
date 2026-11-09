import json
import os

DATA_DIR = "data"


def _load_json(filepath: str, default: [dict, list]) -> dict:
    """
    Загружает JSON-файл.

    Если файла нет, возвращает default.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return default

def _save_json(filepath: str, data: dict):
    """
    Сохраняет данные в JSON-файл.
    """
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def load_metadata(filepath: str) -> dict:
    """
    Загружает метаданные.

    Если файла нет возвращает пустой словарь.
    """
    return _load_json(filepath, {})

def save_metadata(filepath: str, data: dict):
    """
    Сохраняет метаданные.
    """
    _save_json(filepath, data)

def _table_path(table_name: str) -> str:
    """
    Возвращает путь к файлу данных таблицы.
    """
    return os.path.join(DATA_DIR, f"{table_name}.json")

def load_table_data(table_name: str):
    """
    Загружает записи таблицы.

    Если файла нет, возвращает пустой список.
    """
    return _load_json(_table_path(table_name), [])

def save_table_data(table_name, data):
    """
    Сохраняет записи таблицы.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    _save_json(_table_path(table_name), data)
