from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    chat_id: int


class LoginResponse(BaseModel):
    success: bool
    user_id: int | None = None

