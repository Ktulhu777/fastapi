from typing import Optional, Union
from fastapi import Request, HTTPException
from fastapi_users import BaseUserManager, IntegerIDMixin, exceptions, models, schemas

from .database import Users
from config import SECRET
from .service import password_validate

SECRET = SECRET


class UserManager(IntegerIDMixin, BaseUserManager[Users, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def validate_password(self, password: str, user: Union[schemas.UC, models.UP]) -> None:
        if not password_validate.validate(password):
            raise HTTPException(status_code=400, detail="Пароль должен содержать латинские буквы, цифры и спец.символы")

    async def on_after_register(self, user: Users, request: Optional[Request] = None):
        print(f"User {user.username} has registered.")

    async def on_after_request_verify(
            self, user: Users, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.username}. Verification token: {token}")

    async def create(
            self,
            user_create: schemas.UC,
            safe: bool = False,
            request: Optional[Request] = None,
    ) -> models.UP:
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )

        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user
