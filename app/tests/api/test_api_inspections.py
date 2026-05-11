import pytest

from app.services.checkoffice_service import CheckOfficeService


@pytest.mark.asyncio
async def test_inspections_summary_success(client, monkeypatch):
    async def mock_get_inspections_today_summary(*args, **kwargs):
        return {
            "created": 2,
            "process": 3,
            "verification": 1,
            "completed": 4,
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
    assert data["summary"]["created"] == 2
    assert data["summary"]["process"] == 3
    assert data["summary"]["verification"] == 1
    assert data["summary"]["completed"] == 4


@pytest.mark.asyncio
async def test_inspections_summary_empty_result(client, monkeypatch):
    async def mock_get_inspections_today_summary(*args, **kwargs):
        return {
            "created": 0,
            "process": 0,
            "verification": 0,
            "completed": 0,
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


@pytest.mark.asyncio
async def test_inspections_summary_invalid_user_id(client):
    response = await client.get("/checks/today_summary?user_id=wrong")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_inspections_summary_checkoffice_error(client, monkeypatch):
    async def mock_get_inspections_today_summary(*args, **kwargs):
        raise Exception("CheckOffice is unavailable")

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