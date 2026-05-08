def format_today_summary(
    data: dict,
    entity_name: str,
    status_labels: dict[str, str],
    status_emoji: dict[str, str],
) -> str:
    summary = data.get("summary", {})
    lines = []
    for status_code, label in status_labels.items():
        count = summary.get(status_code, 0)
        emoji = status_emoji.get(status_code, "•")
        lines.append(f"{emoji} {label}: {count} {entity_name}")
    return "\n".join(lines)