from fastapi import APIRouter, HTTPException, status

from app.schemas.auth_schemas import LoginRequest, LoginResponse
from app.services.checkoffice_service import CheckOfficeService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest) -> LoginResponse:
    try:
        user = await CheckOfficeService.find_user_by_email(str(data.email))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при запросе к CheckOffice: {str(e)}",
        )

    if user is None:
        return LoginResponse(success=False)

    return LoginResponse(success=True, id=user.id)