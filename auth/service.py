from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from auth.database import Users


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
