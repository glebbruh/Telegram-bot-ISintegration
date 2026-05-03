import datetime

from fastapi import APIRouter, HTTPException, status as http_status

from app.schemas.inspection_schema import (
    InspectionResponse,
    InspectionStatus,
    InspectionSummary,
    InspectionSummaryResponse, InspectionListResponse,
)
from app.services.checkoffice_service import CheckOfficeService

router = APIRouter(prefix="/checks", tags=["inspections"])

@router.get("/today_summary", response_model=InspectionSummaryResponse)
async def get_inspections_today_summary(
    user_id: int | None = None,
) -> InspectionSummaryResponse:
    try:
        summary = await CheckOfficeService.get_inspections_today_summary()
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при запросе к CheckOffice: {str(e)}",
        )

    return InspectionSummaryResponse(summary=InspectionSummary(**summary))



@router.get("", response_model=InspectionListResponse)
async def get_inspections(user_id: int,
                          date_at_from: datetime.date | None = None,
                          date_at_to: datetime.date | None = None,
                          finished_at_from: datetime.date | None = None,
                          finished_at_to: datetime.date | None = None,
                          status: InspectionStatus | None = None,
                          overdue: bool | None = None,
                          pattern_id: int | None = None,
                          show_my: bool = False,
                          made_by_me: bool = False):
    today = datetime.date.today()

    if date_at_from is None and date_at_to is None:
        date_at_from = today
        date_at_to = today
    elif date_at_from is None:
        date_at_from = date_at_to
    elif date_at_to is None:
        date_at_to = date_at_from

    if date_at_from > date_at_to:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="date_at_from не может быть позже date_at_to",
        )

    if finished_at_from is not None and finished_at_to is None:
        finished_at_to = finished_at_from

    if finished_at_to is not None and finished_at_from is None:
        finished_at_from = finished_at_to

    if (
            finished_at_from is not None
            and finished_at_to is not None
            and finished_at_from > finished_at_to
    ):
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="finished_at_from не может быть позже finished_at_to",
        )

    params = {
        "user_id": user_id,
        "i:date_from": f"{date_at_from.isoformat()}T00:00:00",
        "i:date_to": f"{date_at_to.isoformat()}T23:59:59",
        "status": status.value if status is not None else None,
        "overdue": overdue,
        "pattern_id": pattern_id,
        "show_my": show_my,
        "made_by_me": made_by_me,
    }

    if finished_at_from is not None:
        params["finished_at_from"] = f"{finished_at_from.isoformat()}T00:00:00"

    if finished_at_to is not None:
        params["finished_at_to"] = f"{finished_at_to.isoformat()}T23:59:59"

    try:
        checkoffice_inspections = await CheckOfficeService.get_inspections(params)
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при запросе к CheckOffice: {str(e)}",
        )

    response = []

    for inspection in checkoffice_inspections:
        response.append(
            InspectionResponse(
                name=inspection.place.name if inspection.place is not None else "Проверка",
                pattern_name=inspection.pattern.name if inspection.pattern is not None else "",
                status=inspection.status,
                date_at=inspection.date,
                deadline_at=inspection.deadline_at,
            )
        )

    return InspectionListResponse(items=response)
