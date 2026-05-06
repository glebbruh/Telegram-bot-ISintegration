from bot.formatters.dates import format_date
from bot.constants import TASK_PRIORITY_LABELS_LOWER, TASK_STATUS_LABELS, TASK_STATUS_EMOJI

def build_tasks_status_legend() -> str:
    return (
        f"{TASK_STATUS_EMOJI['created']} — {TASK_STATUS_LABELS['created']}\n"
        f"{TASK_STATUS_EMOJI['process']} — {TASK_STATUS_LABELS['process']}\n"
        f"{TASK_STATUS_EMOJI['revise']} — {TASK_STATUS_LABELS['revise']}\n"
        f"{TASK_STATUS_EMOJI['review']} — {TASK_STATUS_LABELS['review']}\n"
        f"{TASK_STATUS_EMOJI['validation']} — {TASK_STATUS_LABELS['validation']}\n"
        f"{TASK_STATUS_EMOJI['completed']} — {TASK_STATUS_LABELS['completed']}\n"
        f"{TASK_STATUS_EMOJI['archived']} — {TASK_STATUS_LABELS['archived']}\n"
        f"{TASK_STATUS_EMOJI['manual_review']} — {TASK_STATUS_LABELS['manual_review']}\n"
        f"{TASK_STATUS_EMOJI['cancelled']} — {TASK_STATUS_LABELS['cancelled']}"
    )

def format_tasks_response(data: dict) -> str:
    items = data.get("items", [])
    if not items:
        return "По вашему запросу задачи не найдены."
    lines = []
    for index, item in enumerate(items, start=1):
        status_code = item.get("status")
        emoji = TASK_STATUS_EMOJI.get(status_code, "▪️")
        name = item.get("name", "Без названия")
        priority_code = item.get("priority")
        priority_label = TASK_PRIORITY_LABELS_LOWER.get(priority_code, "без приоритета")
        deadline_at = format_date(item.get("deadline_at"))
        line = f"{emoji} {index}. {name} — {priority_label} — {deadline_at}"
        lines.append(line)
    return "\n".join(lines)

def format_tasks_response_for_pdf(data: dict) -> str:
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