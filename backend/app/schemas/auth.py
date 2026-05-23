from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str | None = None
    locale: str = "en"
    role: str = "customer"
    is_active: bool = True
    class Config:
        from_attributes = True

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=160)
    locale: str = "en"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
