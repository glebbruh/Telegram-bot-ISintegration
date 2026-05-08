from enum import Enum
from typing import Any

from pydantic import BaseModel

from app.schemas.checkoffice import CheckOfficeInspection, CheckOfficeTask


class WebhookEvent(str, Enum):
    inspection_create = "inspection.create"
    inspection_changeStatus = "inspection.changeStatus"
    task_create = "task.create"
    task_changeStatus = "task.changeStatus"

class InspectionWebhook(BaseModel):
    data: CheckOfficeInspection
    event: WebhookEvent

class TaskWebhook(BaseModel):
    data: CheckOfficeTask
    event: WebhookEvent

class WebhookModel(BaseModel):
    data: dict[str, Any]
    event: WebhookEvent

class WebhookResponse(BaseModel):
    telegram_id: int
    event_type: WebhookEvent
    name: str
    pattern: str | None = None
    status: str
    assignee: bool
    creator: bool