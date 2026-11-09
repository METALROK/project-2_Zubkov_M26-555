import functools


def handle_db_errors(func):
    """
    Перехватывает типичные ошибки БД и выводит понятное сообщение.

    При ошибке обёрнутая функция возвращает None.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as error:
            print(f"Ошибка: таблица или столбец {error} не найден.")
        except ValueError as error:
            print(f"Некорректное значение: {error}.")
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")
        return None

    return wrapper
