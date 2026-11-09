import json
import os

DATA_DIR = "data"


def _load_json(filepath: str, default: dict | list) -> dict:
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

def load_table_data(table_name: str) -> dict:
    """
    Загружает записи таблицы.

    Если файла нет, возвращает пустой список.
    """
    return _load_json(_table_path(table_name), [])

def save_table_data(table_name: str, data: dict):
    """
    Сохраняет записи таблицы.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    _save_json(_table_path(table_name), data)

def delete_table_data(table_name: str):
    """
    Удаляет файл данных таблицы, если он существует.
    """
    try:
        os.remove(_table_path(table_name))
    except FileNotFoundError:
        pass

def create_cacher():
    """
    Создаёт функцию кэширования.

    Кэш хранится в замыкании.
    """
    cache = {}

    def cache_result(key: str, value_func):
        """
        Возвращает результат из кэша или вычисляет его через value_func.
        """
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result

    cache_result.clear = cache.clear
    return cache_result
