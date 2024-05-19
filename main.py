from random import randint

from auth.auth import auth_backend
from auth.database import Users
from auth.schema import UserRead, UserCreate
from auth.manager import fastapi_users, current_user

import aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi import FastAPI, Depends

from redis import Redis
import uuid
from datetime import timedelta

redis = Redis()
app = FastAPI()
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)


@app.get("/code/")
def get_code():
    list_number = [str(randint(0, 9)) for _ in range(6)]
    code = "".join(list_number)
    redis.setex(name=str(uuid.uuid4()), time=timedelta(minutes=30), value=code)
    return code


@app.post("/code/{uid}/")
def code_is_valid(uid: str, code: int):
    code_ex = redis.get(uid)
    if code_ex is not None and code_ex.decode() == str(code):
        return {"success": "Поздравляю вы успешно зарегестрированы"}
    else:
        return {"error": "error"}


@app.get('/code/{uid}/')
def uuid_is_valid(uid: str):
    if redis.get(uid):
        return {"Введите код": 'fsd'}
    else:
        return {"error": "error"}


@app.get("/users/me/")
def protected_route(user: Users = Depends(current_user)):
    return f"Hello, {user.username}"


@app.on_event('startup')
async def startup_event():
    redis = aioredis.from_url('redis://localhost')
    FastAPICache.init(RedisBackend(redis=redis), prefix='fastapi-cache')
