import pytest

from app.services.checkoffice_service import CheckOfficeService


@pytest.mark.asyncio
async def test_tasks_summary_success(client, monkeypatch):
    async def mock_get_tasks_today_summary(*args, **kwargs):
        return {
            "created": 2,
            "process": 3,
            "revise": 1,
            "review": 4,
            "validation": 1,
            "completed": 5,
            "archived": 0,
            "manual_review": 1,
            "cancelled": 0,
        }

    monkeypatch.setattr(
        CheckOfficeService,
        "get_tasks_today_summary",
        mock_get_tasks_today_summary
    )

    response = await client.get("/tasks/today_summary?user_id=41920")

    assert response.status_code == 200

    data = response.json()

    assert "summary" in data
    assert data["summary"]["created"] == 2
    assert data["summary"]["process"] == 3
    assert data["summary"]["revise"] == 1
    assert data["summary"]["review"] == 4
    assert data["summary"]["validation"] == 1
    assert data["summary"]["completed"] == 5
    assert data["summary"]["archived"] == 0
    assert data["summary"]["manual_review"] == 1
    assert data["summary"]["cancelled"] == 0


@pytest.mark.asyncio
async def test_tasks_summary_empty_result(client, monkeypatch):
    async def mock_get_tasks_today_summary(*args, **kwargs):
        return {
            "created": 0,
            "process": 0,
            "revise": 0,
            "review": 0,
            "validation": 0,
            "completed": 0,
            "archived": 0,
            "manual_review": 0,
            "cancelled": 0,
        }

    monkeypatch.setattr(
        CheckOfficeService,
        "get_tasks_today_summary",
        mock_get_tasks_today_summary
    )

    response = await client.get("/tasks/today_summary?user_id=41920")

    assert response.status_code == 200

    data = response.json()

    assert "summary" in data
    assert data["summary"]["created"] == 0
    assert data["summary"]["process"] == 0
    assert data["summary"]["revise"] == 0
    assert data["summary"]["review"] == 0
    assert data["summary"]["validation"] == 0
    assert data["summary"]["completed"] == 0
    assert data["summary"]["archived"] == 0
    assert data["summary"]["manual_review"] == 0
    assert data["summary"]["cancelled"] == 0


@pytest.mark.asyncio
async def test_tasks_summary_invalid_user_id(client):
    response = await client.get("/tasks/today_summary?user_id=abc")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_tasks_summary_checkoffice_error(client, monkeypatch):
    async def mock_get_tasks_today_summary(*args, **kwargs):
        raise Exception("CheckOffice is unavailable")

    monkeypatch.setattr(
        CheckOfficeService,
        "get_tasks_today_summary",
        mock_get_tasks_today_summary
    )

    response = await client.get("/tasks/today_summary?user_id=41920")

    assert response.status_code == 500

    data = response.json()

    assert "detail" in data
    assert "Ошибка при запросе к CheckOffice" in data["detail"]