import os
import httpx

def _backend_base_url() -> str:
    base_url = os.getenv("BACKEND_AUTH_URL", "").strip()
    if not base_url:
        raise RuntimeError("BACKEND_AUTH_URL is not set")
    return base_url.rstrip("/")

def _as_query_value(value):
    if value is None:
        return None
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
    return response.json()

def build_checks_query_params(user_id: int | None, filters: dict) -> dict:
    date_at = filters.get("date_at", {})
    finished_at = filters.get("finished_at", {})
    status = filters.get("status", {})
    overdue = filters.get("overdue", {})
    pattern = filters.get("pattern", {})
    show_my = filters.get("show_my", {})
    made_by_me = filters.get("made_by_me", {})
    params = {
        "user_id": _as_query_value(user_id),
        "date_at_from": _as_query_value(date_at.get("from")),
        "date_at_to": _as_query_value(date_at.get("to")),
        "finished_at_from": _as_query_value(finished_at.get("from")),
        "finished_at_to": _as_query_value(finished_at.get("to")),
        "status": _as_query_value(status.get("value")),
        "overdue": _as_query_value(overdue.get("value")),
        "pattern_id": _as_query_value(pattern.get("id")),
        "show_my": _as_query_value(show_my.get("value", False)),
        "made_by_me": _as_query_value(made_by_me.get("value", False)),
    }
    return {k: v for k, v in params.items() if v is not None}

def build_tasks_query_params(user_id: int | None, filters: dict) -> dict:
    date_period = filters.get("deadline_period", {})
    priority = filters.get("priority", {})
    show_my = filters.get("show_my", {})
    made_by_me = filters.get("made_by_me", {})
    return {
        "user_id": _as_query_value(user_id),
        "date_period_from": _as_query_value(date_period.get("from")),
        "date_period_to": _as_query_value(date_period.get("to")),
        "priority": _as_query_value(priority.get("value")),
        "show_my": _as_query_value(show_my.get("value", False)),
        "made_by_me": _as_query_value(made_by_me.get("value", False)),
    }

async def send_tasks_filters_to_backend(user_id: int | None, filters: dict) -> dict:
    url = f"{_backend_base_url()}/tasks"
    params = build_tasks_query_params(user_id, filters)
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)
    if response.status_code != 200:
        raise RuntimeError(f"Tasks backend error: HTTP {response.status_code}")
    return response.json()

async def send_checks_filters_to_backend(user_id: int | None, filters: dict) -> dict:
    url = f"{_backend_base_url()}/checks"
    params = build_checks_query_params(user_id, filters)
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)
    if response.status_code != 200:
        raise RuntimeError(f"Checks backend error: HTTP {response.status_code}")
    return response.json()

async def fetch_checks_today_summary(user_id: int | None) -> dict:
    url = f"{_backend_base_url()}/checks/today_summary"
    params = {
        "user_id": _as_query_value(user_id),
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)
    if response.status_code != 200:
        raise RuntimeError(f"Checks today summary error: HTTP {response.status_code}")
    return response.json()


async def fetch_tasks_today_summary(user_id: int | None) -> dict:
    url = f"{_backend_base_url()}/tasks/today_summary"
    params = {
        "user_id": _as_query_value(user_id),
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)
    if response.status_code != 200:
        raise RuntimeError(f"Tasks today summary error: HTTP {response.status_code}")
    return response.json()