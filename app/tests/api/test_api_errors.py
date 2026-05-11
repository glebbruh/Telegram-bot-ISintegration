import pytest

from app.services.checkoffice_service import CheckOfficeService


@pytest.mark.asyncio
async def test_tasks_summary_external_system_not_responding(client, monkeypatch):
    async def mock_get_tasks_today_summary(*args, **kwargs):
        raise TimeoutError("External system timeout")

    monkeypatch.setattr(
        CheckOfficeService,
        "get_tasks_today_summary",
        mock_get_tasks_today_summary
    )

    response = await client.get("/tasks/today_summary?user_id=41920")

    assert response.status_code == 500

    data = response.json()

    assert "detail" in data


@pytest.mark.asyncio
async def test_inspections_summary_external_system_not_responding(client, monkeypatch):
    async def mock_get_inspections_today_summary(*args, **kwargs):
        raise TimeoutError("External system timeout")

    monkeypatch.setattr(
        CheckOfficeService,
        "get_inspections_today_summary",
        mock_get_inspections_today_summary
    )

    response = await client.get("/checks/today_summary?user_id=41920")

    assert response.status_code == 500

    data = response.json()

    assert "detail" in data


@pytest.mark.asyncio
async def test_tasks_summary_external_system_returns_error(client, monkeypatch):
    async def mock_get_tasks_today_summary(*args, **kwargs):
        raise Exception("External system error")

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


@pytest.mark.asyncio
async def test_inspections_summary_external_system_returns_error(client, monkeypatch):
    async def mock_get_inspections_today_summary(*args, **kwargs):
        raise Exception("External system error")

    monkeypatch.setattr(
        CheckOfficeService,
        "get_inspections_today_summary",
        mock_get_inspections_today_summary
    )

    response = await client.get("/checks/today_summary?user_id=41920")

    assert response.status_code == 500

    data = response.json()

    assert "detail" in data
    assert "Ошибка при запросе к CheckOffice" in data["detail"]


@pytest.mark.asyncio
async def test_tasks_summary_invalid_external_response_structure(client, monkeypatch):
    async def mock_get_tasks_today_summary(*args, **kwargs):
        return {
            "wrong_field": 123
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
    assert data["summary"]["completed"] == 0


@pytest.mark.asyncio
async def test_inspections_summary_invalid_external_response_structure(client, monkeypatch):
    async def mock_get_inspections_today_summary(*args, **kwargs):
        return {
            "wrong_field": 123
        }

    monkeypatch.setattr(
        CheckOfficeService,
        "get_inspections_today_summary",
        mock_get_inspections_today_summary
    )

    response = await client.get("/checks/today_summary?user_id=41920")

    assert response.status_code == 200

    data = response.json()

    assert "summary" in data
    assert data["summary"]["created"] == 0
    assert data["summary"]["process"] == 0
    assert data["summary"]["verification"] == 0
    assert data["summary"]["completed"] == 0