from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from config.config_redis import cache

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


async def get_login(token: str = Depends(oauth2_scheme)):
    username = cache.get(f'session:{token}:user')
    if token is None:
        raise HTTPException(status_code=401,
                            detail='token not found/has been expired')
    return username
