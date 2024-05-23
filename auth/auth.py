from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport, AuthenticationBackend
from fastapi_users.authentication import JWTStrategy
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from . import service
from .manager import UserManager
from config import SECRET
from .schema import UserRead, UserUpdate, ChangePasswdUser
from .database import Users, get_user_db, get_async_session
from .celery_worker import send_email, redis, redis_2

cookie_transport = CookieTransport(cookie_name='tur', cookie_max_age=3600 * 12)
validate_password = service.ValidateChangePassword()


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[Users, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user()
current_verified_user = fastapi_users.current_user(verified=False)

authAPI = APIRouter()


@authAPI.get("/users/me/", response_model=UserRead)
def profile_user(user: Users = Depends(current_user)):
    return user


@authAPI.put("/users/me/")
async def update_user(user_up: Annotated[UserUpdate, Depends()],
                      user: Users = Depends(current_user),
                      session: AsyncSession = Depends(get_async_session)):
    field = ('username', 'email')
    data_up = {item: getattr(user_up, item) for item in field if getattr(user_up, item) is not None}
    await service.update_user(username_search=user.username,
                              session=session,
                              **data_up)
    return {"success": "Данные успешно обновлены."}


@authAPI.post("/activation-email/", status_code=200)
def activation_user_email(user: Users = Depends(current_verified_user)):
    send_email.delay(user.username, user.email)
    return {"success": "Код успешно отправлен"}


@authAPI.post("/code/", status_code=200)
async def code_is_valid(code: int,
                        user: Users = Depends(current_verified_user),
                        session: AsyncSession = Depends(get_async_session)):
    username = user.username
    code_example = redis.get(username)

    if code_example is not None and code_example.decode() == str(code):
        await service.update_is_verified(username=username, session=session)
        redis.delete(username)
        return {"success": "Поздравляю! Вы успешно подтвердили почту."}
    else:
        raise HTTPException(status_code=400, detail="Подтверждение не прошло.")


@authAPI.patch("/change-password/")
async def change_password(password: Annotated[ChangePasswdUser, Depends()],
                          user: Users = Depends(current_user),
                          session: AsyncSession = Depends(get_async_session)):
    code = redis_2.get(user.email)
    if code is not None and code.decode() == str(password.code):
        if validate_password(password_1=password.new_password, password_2=password.reply_new_password):
            await service.update_password(username=user.username, session=session, password=password.new_password)
            redis.delete(user.email)
            return {"success": "Пароль изменен."}
    raise HTTPException(status_code=404, detail="Пароль не был изменен")


@authAPI.post("/code-password/")
def send_code_change_password(user: Users = Depends(current_user)):
    send_email.delay(user.username, user.email, True)
    return {"success": "Код отправлен на вашу почту."}
