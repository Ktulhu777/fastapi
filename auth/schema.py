from fastapi import HTTPException
from fastapi_users import schemas
from typing import Optional
from pydantic import EmailStr, validator
from password_validator import PasswordValidator

password_validate = PasswordValidator()

password_validate \
    .min(8) \
    .has().digits() \
    .has().letters() \
    .has().symbols()


class UserRead(schemas.BaseUser[int]):
    id: int
    username: str
    email: EmailStr
    is_active: bool = True

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    username: str
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserUpdate(schemas.BaseUserUpdate):
    username: str = None
    email: Optional[EmailStr] = None

    def __getitem__(self, item):
        return item

    # @validator('password')
    # @classmethod
    # def validate_password(cls, value):
    #     if not password_validate.validate(value):
    #         raise HTTPException(status_code=400, detail="Пароль должен содержать латинские буквы, цифры и спец.символы")
    #     return value
