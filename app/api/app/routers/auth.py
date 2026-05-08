from fastapi import APIRouter, HTTPException, status

from psycopg import Error as PsycopgError

from app.schemas.auth_schemas import LoginRequest, LoginResponse
from app.services.checkoffice_service import CheckOfficeService
from app.services.db_service import save_link, delete_link

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

    await save_link(data.chat_id, user.id)

    return LoginResponse(success=True, user_id=user.id)

@router.post("/logout")
async def logout(chat_id: int):
    try:
        await delete_link(chat_id)
    except PsycopgError as e:
        print(f"Ошибка при удалении связи пользователя из БД: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return {"success": True}
