import os
import httpx

def _backend_base_url() -> str:
    base_url = os.getenv("BACKEND_AUTH_URL", "").strip()
    if not base_url:
        raise RuntimeError("BACKEND_AUTH_URL is not set")
    return base_url.rstrip("/")

def _as_query_value(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)

async def fetch_patterns_from_backend(user_id: int) -> list[dict]:
    url = f"{_backend_base_url()}/patterns"
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            url,
            params={"user_id": user_id},
        )
    if response.status_code != 200:
        raise RuntimeError(f"Patterns backend error: HTTP {response.status_code}")
    data = response.json()
    return data.get("patterns", [])

def build_checks_query_params(user_id: int | None, filters: dict) -> dict:
    date_at = filters.get("date_at", {})
    finished_at = filters.get("finished_at", {})
    status = filters.get("status", {})
    overdue = filters.get("overdue", {})
    pattern = filters.get("pattern", {})
    return {
        "user_id": _as_query_value(user_id),
        "date_at_from": _as_query_value(date_at.get("from")),
        "date_at_to": _as_query_value(date_at.get("to")),
        "finished_at_from": _as_query_value(finished_at.get("from")),
        "finished_at_to": _as_query_value(finished_at.get("to")),
        "status": _as_query_value(status.get("value")),
        "overdue": _as_query_value(overdue.get("value")),
        "pattern_id": _as_query_value(pattern.get("id")),
    }

def build_tasks_query_params(user_id: int | None, filters: dict) -> dict:
    date_period = filters.get("deadline_period", {})
    priority = filters.get("priority", {})
    return {
        "user_id": _as_query_value(user_id),
        "date_period_from": _as_query_value(date_period.get("from")),
        "date_period_to": _as_query_value(date_period.get("to")),
        "priority": _as_query_value(priority.get("value")),
    }

async def send_tasks_filters_to_backend(user_id: int | None, filters: dict) -> dict:
    url = f"{BACKEND_AUTH_URL}/tasks"
    date_period = filters.get("deadline_period", {})
    priority = filters.get("priority", {})
    params = {
        "user_id": _as_query_value(user_id),
        "date_period_from": _as_query_value(date_period.get("from")),
        "date_period_to": _as_query_value(date_period.get("to")),
        "priority": _as_query_value(priority.get("value")),
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)
    if response.status_code != 200:
        raise RuntimeError(f"Tasks backend error: HTTP {response.status_code}")
    return response.json()

async def send_checks_filters_to_backend(user_id: int | None, filters: dict) -> dict:
    url = f"{BACKEND_AUTH_URL}/checks"
    params = build_checks_query_params(user_id, filters)
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)
    if response.status_code != 200:
        raise RuntimeError(f"Checks backend error: HTTP {response.status_code}")
    return response.json()

