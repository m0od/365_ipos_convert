from functools import wraps

import jwt
from fastapi import HTTPException, status


def auth_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # print(args)
        req = kwargs['req']
        # res = kwargs['res']
        secret_key = req.app.extra['extra']['secret_key']
        try:
            # print(req.cookies.get('jwt'), secret_key)
            jwt.decode(req.cookies.get('jwt'), secret_key, 'HS256')

        except Exception as ex:
            print(18, ex)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED)
        return await func(*args, **kwargs)


    return wrapper