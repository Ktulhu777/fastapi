from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport, AuthenticationBackend
from fastapi_users.authentication import JWTStrategy
from fastapi import APIRouter, Depends

from auth.manager import UserManager
from config import SECRET
from auth.schema import UserRead
from auth.database import Users, get_user_db
from auth.celery_worker import send_email, redis

cookie_transport = CookieTransport(cookie_name='tur', cookie_max_age=3600 * 12)


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
def protected_route(user: Users = Depends(current_user)):
    return user


@authAPI.post("/activation-email/")
def activation_user_email(user: Users = Depends(current_verified_user)):
    send_email.delay(user.username, user.email)
    return {"success": "Код успешно отправлен"}


@authAPI.post("/code/")
def code_is_valid(code: int, user: Users = Depends(current_verified_user)):
    username = user.username
    code_example = redis.get(username)
    if code_example is not None and code_example.decode() == str(code):
        user.is_verified = True
        redis.delete(username)
        return {"success": "Поздравляю вы успешно зарегистрированы"}
    else:
        return {"error": "Что-то пошло не так"}
