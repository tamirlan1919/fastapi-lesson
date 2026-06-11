from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token
from src.database import get_async_session
from src.redis_client import get_redis
from src.schemas import Token
from src.services.cache_service import CacheService

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/login', response_model=Token, summary="Получить JWT Token")
async def login_for_access_token(
        request: Request,
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_async_session),
        redis: Redis = Depends(get_redis)

):
    client_ip = request.client.host
    cache = CacheService(redis)
    # allowed, attempts = await cache.check_login_rate_limit(client_ip)
    # if not allowed:
    #     raise HTTPException(
    #         status_code=429,
    #         detail=f'Слишком много попыток. Попробуйте через минуту',
    #         headers={'Retry-After': '60'}
    #     )

    user = await authenticate_user(
        username=form_data.username,
        password=form_data.password,
        session=session
    )

    if user is None:
        raise  HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный username или password',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            'sub': user.username,
            'role': user.role
        },
        expires_delta=access_token_expires
    )
    return {
        'access_token': access_token,
        'token_type': 'bearer'
    }

