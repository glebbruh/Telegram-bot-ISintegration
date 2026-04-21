from pydantic import BaseModel, EmailStr


class CheckOfficeUser(BaseModel):
    id: int
    email: EmailStr