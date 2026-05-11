from bot.formatters.dates import format_date
from bot.formatters.checks import (
    format_checks_response,
    format_checks_response_for_pdf,
    get_checks_items,
)
from bot.formatters.tasks import (
    format_tasks_response,
    format_tasks_response_for_pdf,
    get_tasks_items,
)
from bot.formatters.summary import format_today_summary
from bot.constants import (
    CHECK_STATUS_LABELS,
    CHECK_STATUS_EMOJI,
    TASK_STATUS_LABELS,
    TASK_STATUS_EMOJI,
)


def test_format_date_iso():
    assert format_date("2026-05-10") == "10.05.2026"


def test_format_date_empty():
    assert format_date(None) == "—"
    assert format_date("null") == "—"


def test_format_checks_response_with_items():
    data = {
        "items": [
            {
                "name": "Проверка склада",
                "pattern_name": "Плановая проверка",
                "status": "process",
                "date_at": "2026-05-10",
                "deadline_at": "2026-05-12",
            }
        ]
    }

    result = format_checks_response(data)

    assert "Проверка склада" in result
    assert "Плановая проверка" in result
    assert "10.05.2026" in result
    assert "12.05.2026" in result
    assert "☑️" in result

def test_format_checks_response_empty():
    assert format_checks_response({"items": []}) == "По вашему запросу проверки не найдены."

def test_get_checks_items():
    data = {"items": [{"name": "A"}]}
    assert get_checks_items(data) == [{"name": "A"}]

def test_format_checks_response_for_pdf_without_emoji():
    data = {
        "items": [
            {
                "name": "Проверка склада",
                "pattern_name": "Плановая проверка",
                "status": "process",
                "date_at": "2026-05-10",
                "deadline_at": "2026-05-12",
            }
        ]
    }
    result = format_checks_response_for_pdf(data)
    assert "В работе" in result
    assert "☑️" not in result

def test_format_tasks_response_with_emoji():
    data = {
        "items": [
            {
                "name": "Подготовить отчет",
                "status": "completed",
                "priority": "high",
                "deadline_at": "2026-05-10",
            }
        ]
    }
    result = format_tasks_response(data)
    assert "Подготовить отчет" in result
    assert "высокий" in result
    assert "10.05.2026" in result
    assert "✅" in result

def test_format_tasks_response_for_pdf_without_emoji():
    data = {
        "items": [
            {
                "name": "Подготовить отчет",
                "status": "completed",
                "priority": "high",
                "deadline_at": "2026-05-10",
            }
        ]
    }
    result = format_tasks_response_for_pdf(data)
    assert "Завершено" in result
    assert "✅" not in result

def test_get_tasks_items():
    data = {"items": [{"name": "Task"}]}
    assert get_tasks_items(data) == [{"name": "Task"}]

def test_format_today_summary_checks():
    data = {
        "summary": {
            "created": 2,
            "process": 3,
            "completed": 4,
            "verification": 1,
        }
    }
    result = format_today_summary(
        data,
        "проверок",
        CHECK_STATUS_LABELS,
        CHECK_STATUS_EMOJI,
    )

    assert "⚪ Назначено: 2 проверок" in result
    assert "☑️ В работе: 3 проверок" in result
    assert "✅ Завершено: 4 проверок" in result
    assert "⚠️ Валидация: 1 проверок" in result

def test_format_today_summary_tasks():
    data = {
        "summary": {
            "created": 1,
            "process": 2,
            "completed": 3,
        }
    }
    result = format_today_summary(
        data,
        "задач",
        TASK_STATUS_LABELS,
        TASK_STATUS_EMOJI,
    )
    assert "⚪ Назначено: 1 задач" in result
    assert "☑️ В работе: 2 задач" in result
    assert "✅ Завершено: 3 задач" in result