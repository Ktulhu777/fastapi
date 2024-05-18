from fastapi_users import schemas
from typing import Optional
from pydantic import EmailStr
from sqlalchemy.orm import Mapped


class UserRead(schemas.BaseUser[int]):
    id: int
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    username: str
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserUpdate(schemas.BaseUserUpdate):
    id: int
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: bool = False
