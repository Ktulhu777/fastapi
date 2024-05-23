from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from password_validator import PasswordValidator
from fastapi_users import BaseUserManager

from .database import Users

password_validate = PasswordValidator()

password_validate \
    .min(8) \
    .has().digits() \
    .has().letters() \
    .has().symbols()


async def update_is_verified(username: str,
                             session: AsyncSession) -> None:
    try:
        await session.execute(
            update(Users)
            .where(Users.username == username)
            .values(is_verified=True)
        )
        await session.commit()
    except Exception:
        await session.rollback()
        raise HTTPException(status_code=404)


async def update_user(username_search: str, session: AsyncSession, **kwargs):
    try:
        await session.execute(
            update(Users)
            .where(Users.username == username_search)
            .values(**kwargs)
        )
        await session.commit()
    except Exception:
        await session.rollback()
        raise HTTPException(status_code=404)


async def update_password(username: str, session: AsyncSession, password: str):
    hashed = BaseUserManager(Users)
    try:
        await session.execute(
            update(Users)
            .where(Users.username == username)
            .values(hashed_password=hashed.password_helper.hash(password))
        )
        await session.commit()

    except Exception:
        await session.rollback()
        raise HTTPException(status_code=404)


class ValidateChangePassword:
    def __call__(self, password_1: str, password_2: str):
        if password_1 != password_2:
            raise HTTPException(status_code=400, detail="Пароли не равны")
        if not password_validate.validate(password_1):
            raise HTTPException(status_code=400, detail="Пароль должен содержать латинские буквы, цифры и спец.символы")
        return True
