from typing import List
from fastapi import APIRouter, HTTPException
from src.schemas import UserCreate, UserInDB, UserResponse

router = APIRouter(
    prefix='/users',
    tags=['Пользователи']
)

users_db: dict[str, UserInDB] = {
    'admin': UserInDB(
        id = 1,
        username='admin',
        email='admin@inbox.com',
        password='admin123',
        role='admin'
    )
}

ID: int = 1


@router.post('/register', status_code=201, summary='Зарегистрировать пользователя')
async def register_user(user_data: UserCreate):
    if user_data.username in users_db:
        raise HTTPException(
            status_code=409,
            detail=f'Пользователь {user_data.username} уже существутет'
        )
    global ID
    ID += 1
    user = UserInDB(
        id = ID,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        role='user'
    )
    users_db[user_data.username] = user

    return user


@router.get('/', response_model=List[UserResponse], summary='Получить список пользователей')
async def get_users():
    return list(users_db.values())

