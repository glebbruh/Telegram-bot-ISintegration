from datetime import datetime

CHECK_STATUS_EMOJI = {
    "process": "☑️",
    "completed": "✅",
    "verification": "⚠️",
    "created": "⚪",
}

CHECK_STATUS_LABELS = {
    "process": "в работе",
    "completed": "завершено",
    "verification": "валидация",
    "created": "назначено",
}

TASK_STATUS_LABELS = {
    "process": "в работе",
    "completed": "завершено",
    "verification": "валидация",
    "created": "назначено",
}

TASK_PRIORITY_LABELS = {
    "none": "без приоритета",
    "low": "низкий",
    "medium": "средний",
    "high": "высокий",
}

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

def format_tasks_response(data: dict) -> str:
    items = data.get("items", [])
    if not items:
        return "По вашему запросу задачи не найдены."
    lines = []
    for index, item in enumerate(items, start=1):
        status_code = item.get("status")
        status_label = TASK_STATUS_LABELS.get(status_code, "без статуса")
        name = item.get("name", "Без названия")
        priority_code = item.get("priority")
        priority_label = TASK_PRIORITY_LABELS.get(priority_code, "без приоритета")
        deadline_period = format_period(item.get("deadline_period"))
        line = f"{status_label} {index}. {name} — {priority_label} — {deadline_period}"
        lines.append(line)
    return "\n".join(lines)