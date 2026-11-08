import json


def load_metadata(filepath: str) -> dict:
    """
    Загружает данные из JSON-файла.

    Если файла нет возвращает пустой словарь.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_metadata(filepath, data):
    """
    Сохраняет метаданные в JSON-файл.
    """
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
