from bot.formatters.dates import format_date
from bot.constants import TASK_PRIORITY_LABELS_LOWER, TASK_STATUS_LABELS

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
        priority_label = TASK_PRIORITY_LABELS_LOWER.get(priority_code, "без приоритета")
        deadline_at = format_date(item.get("deadline_at"))
        line = f"{status_label} {index}. {name} — {priority_label} — {deadline_at}"
        lines.append(line)
    return "\n".join(lines)

def get_tasks_items(data: dict) -> list[dict]:
    return data.get("items", [])