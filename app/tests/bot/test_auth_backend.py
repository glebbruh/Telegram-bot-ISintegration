import pytest

from bot.handlers.auth import send_auth_to_backend

@pytest.mark.asyncio
async def test_send_auth_to_backend_success(monkeypatch, httpx_mock):
    monkeypatch.setenv("BACKEND_AUTH_URL", "http://testserver")
    httpx_mock.add_response(
        method="POST",
        url="http://testserver/auth/login",
        json={
            "success": True,
            "user_id": 42,
        },
        status_code=200,
    )
    result = await send_auth_to_backend(
        email="user@example.com",
        chat_id=123456789,
        password="secret",
    )
    assert result == {
        "success": True,
        "user_id": 42,
    }
    request = httpx_mock.get_request()
    assert request.url == "http://testserver/auth/login"
    assert request.method == "POST"
    assert request.read() == b'{"email":"user@example.com","chat_id":123456789,"password":"secret"}'

@pytest.mark.asyncio
async def test_send_auth_to_backend_failed_auth(monkeypatch, httpx_mock):
    monkeypatch.setenv("BACKEND_AUTH_URL", "http://testserver")
    httpx_mock.add_response(
        method="POST",
        url="http://testserver/auth/login",
        json={
            "success": False,
            "user_id": None,
        },
        status_code=200,
    )
    result = await send_auth_to_backend(
        email="bad@example.com",
        chat_id=123456789,
        password="wrong",
    )
    assert result == {
        "success": False,
        "user_id": None,
    }