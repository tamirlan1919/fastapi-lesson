import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from src.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import UserInDB
from src.repositories.users_repo import UserRepository

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

pwd_context = CryptContext(
    schemes=['pbkdf2_sha256', 'bcrypt'],
    deprecated='auto'
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except UnknownHashError:
        return False


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
            algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        return None


async def authenticate_user(username: str, password: str, session: AsyncSession) -> Optional[UserInDB]:
    repo = UserRepository(session)
    user = await repo.get_user_by_username(username=username)

    if not verify_password(password, user.hashed_password):
        return None

    return UserInDB(
        id=user.id,
        username=user.username,
        email=user.email,
        hashed_password=user.hashed_password
    )


async def get_current_user(token: str = Depends(oauth2_scheme),
                           session: AsyncSession = Depends(get_async_session)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Не удалость проверить токен',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    username: str | None = payload.get('sub')

    if username is None:
        raise credentials_exception

    repo = UserRepository(session)
    user = await repo.get_user_by_username(username=username)

    if user is None:
        raise credentials_exception

    return UserInDB(
        id=user.id,
        username=user.username,
        email=user.email,
        hashed_password=user.hashed_password
    )


def require_role(required_role: str):
    async def role_checker(current_user: UserInDB = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Недостаточно прав для выполнения действий'
            )

        return current_user

    return Depends(role_checker)
