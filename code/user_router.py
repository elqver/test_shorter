import hashlib
import secrets

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from config.config_redis import cache
from config.env import SALT
from schemas import LogInResponse

user_router = APIRouter()


@user_router.post("/register")
async def register(username: str, password: str):
    if cache.get(f'user:{username}:password_hash'):
        raise HTTPException(status_code=400,
                            detail=f'user with {username=} already exists')
    cache.set(f'user:{username}:password_hash',
              hashlib.sha256((SALT + password).encode()).hexdigest())
    return {'username': username}


@user_router.post("/login")
async def log_in(form_data: OAuth2PasswordRequestForm = Depends()):
    user_password_hash: bytes | None = cache.get(
        f'user:{form_data.username}:password_hash')
    if user_password_hash is None or user_password_hash.decode(
    ) != hashlib.sha256((SALT + form_data.password).encode()).hexdigest():
        raise HTTPException(status_code=400,
                            detail='login and password do not match')
    token = secrets.token_urlsafe(50)
    cache.set(f'session:{token}:user', form_data.username, ex=300)
    return LogInResponse(access_token=token)
