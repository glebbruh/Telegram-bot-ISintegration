from fastapi import APIRouter, HTTPException, status

from app.schemas.inspection_schema import Pattern
from app.services.checkoffice_service import CheckOfficeService

router = APIRouter(prefix="/patterns", tags=["patterns"])

@router.get("", response_model=list[Pattern])
async def patterns():
    try:
        return_patterns = await CheckOfficeService.get_patterns()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при запросе к CheckOffice: {str(e)}",
        )

    return return_patterns
