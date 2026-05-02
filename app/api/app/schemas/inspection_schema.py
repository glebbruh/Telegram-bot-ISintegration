import datetime
from enum import Enum

from pydantic import BaseModel


class PlaceGroupsSchema(BaseModel):
    id: int
    name: str

class PlaceSchema(BaseModel):
    name: str
    groups: list[PlaceGroupsSchema] = []

class Pattern(BaseModel):
    id: int
    name: str

class InspectionStatus(str, Enum):
    created = "created"
    process = "process"
    verification = "verification"
    completed = "completed"

class InspectionResponse(BaseModel):
    name: str
    pattern_name: str
    status: InspectionStatus
    date_at: datetime.datetime | None = None
    deadline_at: datetime.datetime | None = None

class InspectionSummary(BaseModel):
    created: int = 0
    process: int = 0
    verification: int = 0
    completed: int = 0

class InspectionSummaryResponse(BaseModel):
    summary: InspectionSummary
