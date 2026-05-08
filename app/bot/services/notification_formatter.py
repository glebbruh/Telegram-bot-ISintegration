from bot.schemas.webhook_events import BotWebhookPayload, WebhookEvent
from bot.constants import CHECK_STATUS_LABELS_LOWER, TASK_STATUS_LABELS_LOWER

def build_notification_text(payload: BotWebhookPayload) -> str:
    if payload.event_type == WebhookEvent.task_change_status:
        status_label = TASK_STATUS_LABELS_LOWER[payload.status]
        return f'⚠️ У задачи "{payload.name}" изменился статус на "{status_label}".'
    if payload.event_type == WebhookEvent.inspection_change_status:
        status_label = CHECK_STATUS_LABELS_LOWER[payload.status]
        return f'⚠️ У проверки "{payload.name}" изменился статус на "{status_label}".'
    if payload.event_type == WebhookEvent.task_create:
        if payload.assignee:
            return f'📌 Вам назначили новую задачу "{payload.name}"'
        if payload.creator:
            return f'📌 Вы назначили новую задачу "{payload.name}"'
        return f'📌 Добавлена новая задача "{payload.name}"'
    if payload.event_type == WebhookEvent.inspection_create:
        if payload.assignee:
            return f'📌 Вам назначили новую проверку "{payload.name}"'
        if payload.creator:
            return f'📌 Вы назначили новую проверку "{payload.name}"'
        return f'📌 Добавлена новая проверка "{payload.name}"'
    return "Получено новое уведомление."