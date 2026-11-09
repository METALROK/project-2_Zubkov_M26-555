QUOTES = "\"'"


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
