import datetime

from pydantic import BaseModel, EmailStr

from app.schemas.inspection_schema import InspectionStatus, PlaceSchema, Pattern, PlaceGroupsSchema
from app.schemas.task_schema import TaskStatus, TaskPriority


class CheckOfficeUser(BaseModel):
    id: int
    email: EmailStr

class CheckOfficeInspection(BaseModel):
    status: InspectionStatus
    date: datetime.datetime
    deadline_at: datetime.datetime
    started_at: datetime.datetime | None = None
    finished_at: datetime.datetime | None = None
    place: PlaceSchema
    pattern: Pattern

    assignee: CheckOfficeUser | None = None
    creator: CheckOfficeUser | None = None

class CheckOfficeTask(BaseModel):
    title: str
    status: TaskStatus
    priority: TaskPriority | None = None
    expire_at: datetime.datetime | None = None
    assignee: CheckOfficeUser | None = None
    creator: CheckOfficeUser | None = None




