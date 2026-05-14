import os
from fastapi import APIRouter, HTTPException

from src.auth import hash_password
from src.repositories.users_repo import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    seed_admin,
    users_db,
)
from src.schemas import UserCreate, UserResponse

router = APIRouter(
    prefix='/users',
    tags=['Пользователи']
)

ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
seed_admin(hashed_password=hash_password(ADMIN_PASSWORD))


@router.post('/register', status_code=201, summary='Зарегистрировать пользователя')
async def register_user(user_data: UserCreate):
    if get_user_by_email(user_data.email) is not None:
        raise HTTPException(
            status_code=409,
            detail=f'Пользователь {user_data.username} уже существутет'
        )
    if get_user_by_username(user_data.username) is not None:
        raise HTTPException(
            status_code=400,
            detail='Username already exists'
        )
    user = create_user(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role='user'
    )
    return user


@router.get('/', response_model=list[UserResponse], summary='Получить список пользователей')
async def get_users():
    return list(users_db.values())
