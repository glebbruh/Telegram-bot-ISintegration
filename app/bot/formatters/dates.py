from datetime import datetime

def format_date(value: str | None) -> str:
    if not value or value == "null":
        return "—"
    try:
        return datetime.fromisoformat(value).strftime("%d.%m.%Y")
    except ValueError:
        return str(value)

def format_period(period: dict | None) -> str:
    if not period:
        return "—"
    date_from = format_date(period.get("from"))
    date_to = format_date(period.get("to"))
    if date_from == "—" and date_to == "—":
        return "—"
    return f"{date_from} - {date_to}"