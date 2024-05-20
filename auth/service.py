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
        raise HTTPException
