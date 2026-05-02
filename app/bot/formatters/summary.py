from bot.constants import CHECK_STATUS_LABELS_LOWER, TASK_STATUS_LABELS

def format_today_summary(
    data: dict,
    entity_name: str,
    status_labels: dict[str, str],
) -> str:
    summary = data.get("summary", {})
    lines = []
    for status_code, label in status_labels.items():
        count = summary.get(status_code, 0)
        lines.append(f"{count} {entity_name} {label}")
    return "\n".join(lines)