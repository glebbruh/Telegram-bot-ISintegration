import datetime
from enum import Enum

from pydantic import BaseModel


class TaskStatus(str, Enum):
    created = "created"
    process = "process"
    revise = "revise"
    review = "review"
    validation = "validation"
    completed = "completed"
    archived = "archived"
    manual_review = "manual_review"
    cancelled = "cancelled"

class TaskPriority(str, Enum):
    normal = "normal"
    high = "high"
    low = "low"

class TaskResponse(BaseModel):
    name: str
    status: TaskStatus
    priority: TaskPriority | None = None
    deadline: datetime.datetime | None = None

class TaskSummary(BaseModel):
    created: int = 0
    process: int = 0
    revise: int = 0
    review: int = 0
    validation: int = 0
    completed: int = 0
    archived: int = 0
    manual_review: int = 0
    cancelled: int = 0


class TaskSummaryResponse(BaseModel):
    summary: TaskSummary



