from datetime import datetime

def expiration(value: str | None) -> int | None:
    if value is None:
        return None

    if value.isdigit():
        return int(value)

    return int(datetime.fromisoformat(value).timestamp())
