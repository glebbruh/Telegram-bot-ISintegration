import datetime

from fastapi import APIRouter, HTTPException, status

from app.schemas.checkoffice import CheckOfficeTask
from app.schemas.task_schema import TaskPriority, TaskSummaryResponse, TaskSummary
from app.services.checkoffice_service import CheckOfficeService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/today_summary", response_model=TaskSummaryResponse)
async def get_tasks_today_summary(user_id: int | None = None) -> TaskSummaryResponse:
    try:
        summary = await CheckOfficeService.get_tasks_today_summary()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при запросе к CheckOffice: {str(e)}",
        )

    return TaskSummaryResponse(summary=TaskSummary(**summary))


@router.get("", response_model=list[CheckOfficeTask])
async def tasks(user_id: int,
                priority: TaskPriority | None = None,
                date_period_from: datetime.date | None = None,
                date_period_to: datetime.date | None = None,
                show_my: bool = True,
                made_by_me: bool = False) -> list[CheckOfficeTask]:

    if date_period_from is None:
        date_period_from = datetime.date.today()
    if date_period_to is None:
        date_period_to = datetime.date.today()

    deadline_from = f"{date_period_from.isoformat()}T00:00:00"
    deadline_to = f"{date_period_to.isoformat()}T23:59:59"
    params = {
        "user_id": user_id,
        "t:deadline_at_from": deadline_from,
        "t:deadline_at_to": deadline_to,
        "priority": priority.value if priority is not None else None,
        "show_my": show_my,
        "made_by_me": made_by_me,
    }

    try:
        return_tasks = await CheckOfficeService.get_tasks(params)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при запросе к CheckOffice: {str(e)}",
        )

    return return_tasks


