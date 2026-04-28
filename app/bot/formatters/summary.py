from bot.constants import CHECK_STATUS_LABELS_LOWER

def format_today_summary(data:dict, entity_name: str) -> str:
    summary = data.get("summary", {})
    completed = summary.get("completed", 0)
    process = summary.get("process", 0)
    verification = summary.get("verification", 0)
    created = summary.get("created", 0)
    return (
        f"{completed} {entity_name} {CHECK_STATUS_LABELS_LOWER['completed']}\n"
        f"{process} {CHECK_STATUS_LABELS_LOWER['process']}\n"
        f"{verification} {CHECK_STATUS_LABELS_LOWER['verification']}\n"
        f"{created} {CHECK_STATUS_LABELS_LOWER['created']}"
    )