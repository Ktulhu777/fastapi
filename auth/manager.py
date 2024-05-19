from typing import Optional, Union
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, exceptions, models, schemas, FastAPIUsers

from auth.auth import auth_backend
from config import SECRET
from auth.database import Users, get_user_db
from auth.schema import password_validate

SECRET = SECRET


class UserManager(IntegerIDMixin, BaseUserManager[Users, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def validate_password(self, password: str, user: Union[schemas.UC, models.UP]) -> None:
        if not password_validate.validate(password):
            raise ValueError("Пароль должен содержать латинские буквы, цифры и спец.символы")

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
        # user_dict["is_active"] = False

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        # send_email.delay(user_dict['username'])

        return created_user


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[Users, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user()
