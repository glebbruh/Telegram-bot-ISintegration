from bot.schemas.webhook_events import BotWebhookPayload
from bot.services.notification_formatter import build_notification_text

def test_task_status_change_notification():
    payload = BotWebhookPayload(
        chat_id=123,
        event_type="task.changeStatus",
        name="Подготовить отчет",
        status="process",
        assignee=True,
        creator=False,
    )
    text = build_notification_text(payload)
    assert text == '⚠️ У задачи "Подготовить отчет" изменился статус на "в работе".'

def test_inspection_status_change_notification():
    payload = BotWebhookPayload(
        chat_id=123,
        event_type="inspection.changeStatus",
        name="Проверка склада",
        pattern="Плановая проверка",
        status="completed",
        assignee=True,
        creator=False,
    )
    text = build_notification_text(payload)
    assert text == '⚠️ У проверки "Проверка склада" изменился статус на "завершено".'

def test_task_create_for_assignee():
    payload = BotWebhookPayload(
        chat_id=123,
        event_type="task.create",
        name="Подготовить отчет",
        status=None,
        assignee=True,
        creator=False,
    )
    text = build_notification_text(payload)
    assert text == '📌 Вам назначили новую задачу "Подготовить отчет"'

def test_task_create_for_creator():
    payload = BotWebhookPayload(
        chat_id=123,
        event_type="task.create",
        name="Подготовить отчет",
        status=None,
        assignee=False,
        creator=True,
    )
    text = build_notification_text(payload)
    assert text == '📌 Вы назначили новую задачу "Подготовить отчет"'

def test_inspection_create_for_assignee():
    payload = BotWebhookPayload(
        chat_id=123,
        event_type="inspection.create",
        name="Проверка склада",
        pattern="Плановая проверка",
        status=None,
        assignee=True,
        creator=False,
    )
    text = build_notification_text(payload)
    assert text == '📌 Вам назначили новую проверку "Проверка склада"'