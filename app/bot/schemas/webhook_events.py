from enum import Enum
from pydantic import BaseModel

class WebhookEvent(str, Enum):
    inspection_create = "inspection.create"
    inspection_change_status = "inspection.changeStatus"
    task_create = "task.create"
    task_change_status = "task.changeStatus"

class BotWebhookPayload(BaseModel):
    chat_id: int
    event_type: WebhookEvent
    name: str
    pattern: str | None = None
    status: str | None = None
    assignee: bool = False
    creator: bool = False