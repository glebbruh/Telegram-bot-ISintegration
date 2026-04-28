from bot.formatters.dates import format_date
from bot.constants import CHECK_STATUS_EMOJI, CHECK_STATUS_LABELS

def build_checks_status_legend() -> str:
    return (
        f"{CHECK_STATUS_EMOJI['process']} — {CHECK_STATUS_LABELS['process']}\n"
        f"{CHECK_STATUS_EMOJI['completed']} — {CHECK_STATUS_LABELS['completed']}\n"
        f"{CHECK_STATUS_EMOJI['verification']} — {CHECK_STATUS_LABELS['verification']}\n"
        f"{CHECK_STATUS_EMOJI['created']} — {CHECK_STATUS_LABELS['created']}"
    )

def format_checks_response(data: dict) -> str:
    items = data.get("items", [])
    if not items:
        return "По вашему запросу проверки не найдены."
    lines = []
    for index, item in enumerate(items, start=1):
        status = item.get("status")
        emoji = CHECK_STATUS_EMOJI.get(status, "▪️")
        name = item.get("name", "Без названия")
        pattern_name = item.get("pattern_name", "Без шаблона")
        date_at = format_date(item.get("date_at"))
        deadline_at = format_date(item.get("deadline_at"))
        line = (
            f"{emoji} {index}. {name} — {pattern_name} — "
            f"плановое начало ({date_at}) — "
            f"плановое завершение ({deadline_at})"
        )
        lines.append(line)
    return "\n".join(lines)

def get_checks_items(data: dict) -> list[dict]:
    return data.get("checks", data.get("items", []))