from datetime import datetime

def format_date(value: str | None) -> str:
    if not value or value == "null":
        return "—"
    try:
        return datetime.fromisoformat(value).strftime("%d.%m.%Y")
    except ValueError:
        return str(value)