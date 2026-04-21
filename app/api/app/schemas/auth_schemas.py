from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    telegram_id: int


class LoginResponse(BaseModel):
    success: bool

