from bot.services.connect_with_backend import (
    _as_query_value,
    build_checks_query_params,
    build_tasks_query_params,
)

def test_as_query_value_none():
    assert _as_query_value(None) is None

def test_as_query_value_bool():
    assert _as_query_value(True) == "true"
    assert _as_query_value(False) == "false"

def test_as_query_value_string():
    assert _as_query_value("process") == "process"

def test_build_checks_query_params_full():
    filters = {
        "date_at": {"from": "2026-05-01", "to": "2026-05-02"},
        "finished_at": {"from": "2026-05-03", "to": "2026-05-04"},
        "status": {"value": "process"},
        "overdue": {"value": True},
        "pattern": {"id": 15},
        "show_my": {"value": True},
        "made_by_me": {"value": False},
    }
    params = build_checks_query_params(42, filters)
    assert params == {
        "user_id": "42",
        "date_at_from": "2026-05-01",
        "date_at_to": "2026-05-02",
        "finished_at_from": "2026-05-03",
        "finished_at_to": "2026-05-04",
        "status": "process",
        "overdue": "true",
        "pattern_id": "15",
        "show_my": "true",
        "made_by_me": "false",
    }

def test_build_checks_query_params_removes_empty_values():
    filters = {
        "status": {},
        "overdue": {},
        "pattern": {},
        "show_my": {"value": False},
        "made_by_me": {"value": False},
    }
    params = build_checks_query_params(42, filters)
    assert "status" not in params
    assert "overdue" not in params
    assert "pattern_id" not in params
    assert params["show_my"] == "false"
    assert params["made_by_me"] == "false"

def test_build_tasks_query_params_full():
    filters = {
        "deadline_period": {"from": "2026-05-01", "to": "2026-05-05"},
        "priority": {"value": "high"},
        "show_my": {"value": True},
        "made_by_me": {"value": False},
    }
    params = build_tasks_query_params(42, filters)
    assert params == {
        "user_id": "42",
        "date_period_from": "2026-05-01",
        "date_period_to": "2026-05-05",
        "priority": "high",
        "show_my": "true",
        "made_by_me": "false",
    }

def test_build_tasks_query_params_removes_empty_priority_and_dates():
    filters = {
        "deadline_period": {},
        "priority": {},
        "show_my": {"value": False},
        "made_by_me": {"value": True},
    }
    params = build_tasks_query_params(42, filters)
    assert "date_period_from" not in params
    assert "date_period_to" not in params
    assert "priority" not in params
    assert params["show_my"] == "false"
    assert params["made_by_me"] == "true"