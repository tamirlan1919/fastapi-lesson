from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from src.routers.users import users_db
from src.schemas import UserInDB


SECRET_KEY = 'super_secret_key_change_me_in_production'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES=30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    if expires_delta is None:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    else:
        expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({'exp': expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM

    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=ALGORITHM
        )
        return payload
    except JWTError:
        return None


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = users_db.get(username)

    if user is None:
        return None

    if user.password != password:
        return None

    return user


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Не удалость проверить токен',
        headers={'WWW-Authenticate': 'Bearer'}
    )

    payload = decode_access_token(token)


    if payload in None:
        raise credentials_exception

    username: str | None = payload.get('sub')

    if username is None:
        raise credentials_exception

    user = users_db.get(username)

    if user in None:
        raise credentials_exception

    return user


def require_role(required_role: str):
    async def role_checker(current_user: UserInDB = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Недостаточно прав для выполнения действий')

        return current_user
    return Depends(role_checker)
