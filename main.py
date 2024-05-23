from auth import auth
from auth.schema import UserRead, UserCreate
from auth.auth import fastapi_users

import uvicorn
import aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi import FastAPI

app = FastAPI()

app.include_router(auth.authAPI,
                   prefix="/auth",
                   tags=["auth"])

app.include_router(
    fastapi_users.get_auth_router(auth.auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)


app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)


@app.on_event('startup')
async def startup_event():
    redis = aioredis.from_url('redis://localhost')
    FastAPICache.init(RedisBackend(redis=redis), prefix='fastapi-cache')


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
