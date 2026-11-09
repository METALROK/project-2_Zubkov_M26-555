from primitive_db.constants import QUOTES


def _split_outside_quotes(text: str, separator: str=",") -> list:
    """
    Делит строку по разделителю, игнорируя разделители внутри кавычек.
    """
    parts = []
    current = []
    quote = None

    for char in text:
        if quote:
            if char == quote:
                quote = None
        elif char in QUOTES:
            quote = char
        elif char == separator:
            parts.append("".join(current))
            current = []
            continue
        current.append(char)

    if quote:
        raise ValueError(text.strip())

    parts.append("".join(current))
    return parts

def parse_value(raw: str) -> int | str | bool:
    """
    Превращает текст значения в str, bool или int.

    Иначе выбрасывает ValueError.
    """
    raw = raw.strip()

    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in QUOTES:
        return raw[1:-1]

    if raw.lower() in ("true", "false"):
        return raw.lower() == "true"

    try:
        return int(raw)
    except ValueError:
        raise ValueError(raw) from None

def parse_condition(text: str) -> dict:
    """
    Разбирает текст на составляющие.
    """
    column, separator, raw_value = text.partition("=")
    column = column.strip()

    if not separator or not column or not raw_value.strip():
        raise ValueError(text.strip())

    return {column: parse_value(raw_value)}

def parse_where(text: str) -> dict:
    """
    Разбирает условие where на составляющие.
    """
    return parse_condition(text)

def parse_set(text: str) -> dict:
    """
    Разбирает операцию set на составляющие.
    """
    result = {}
    for part in _split_outside_quotes(text):
        result.update(parse_condition(part))
    return result

def parse_values(text: str) -> list:
    """
    Разбирает набор значений на фрагменты и составляет список.
    """
    text = text.strip()

    if not (text.startswith("(") and text.endswith(")")):
        raise ValueError(text)

    inner = text[1:-1]
    if not inner.strip():
        return []

    return [parse_value(part) for part in _split_outside_quotes(inner)]

def _strip_keyword(text: str, keyword: str) -> str:
    """
    Отрезает ключевое слово в начале строки.

    Если его нет, выбрасывает ValueError.
    """
    text = text.strip()
    if not text.startswith(keyword):
        raise ValueError(text)
    return text[len(keyword):].strip()

def parse_insert(user_input: str) -> tuple:
    """
    Разбирает insert-запрос на составляющие.
    """
    words = user_input.split(maxsplit=3)
    if len(words) != 4 or words[1] != "into":
        raise ValueError(user_input)
    return words[2], _strip_keyword(words[3], "values")

def parse_select(user_input: str) -> tuple:
    """
    Разбирает select-запрос на составляющие.
    """
    words = user_input.split(maxsplit=3)
    if len(words) < 3 or words[1] != "from":
        raise ValueError(user_input)
    where_text = _strip_keyword(words[3], "where") if len(words) == 4 else None
    return words[2], where_text

def parse_update(user_input: str) -> tuple:
    """
    Разбирает update-запрос на составляющие.
    """
    words = user_input.split(maxsplit=2)
    if len(words) != 3:
        raise ValueError(user_input)
    set_text, separator, where_text = _strip_keyword(words[2], "set").partition(
        " where "
    )
    if not separator:
        raise ValueError(user_input)
    return words[1], set_text, where_text

def parse_delete(user_input: str) -> tuple:
    """
    Разбирает delete-запрос на составляющие.
    """
    words = user_input.split(maxsplit=3)
    if len(words) != 4 or words[1] != "from":
        raise ValueError(user_input)
    return words[2], _strip_keyword(words[3], "where")
