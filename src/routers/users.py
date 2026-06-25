from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from src.auth import hash_password, get_current_user
from src.database import get_async_session
from src.schemas import UserCreate, UserResponse, UserInDB
from src.repositories.users_repo import UserRepository


router = APIRouter(
    prefix='/users',
    tags=['Пользователи']
)


@router.post('/register', status_code=201, summary='Зарегистрировать пользователя', response_model=UserResponse)
async def register_user(user_data: UserCreate,
                        session: AsyncSession = Depends(get_async_session)):
    repo = UserRepository(session)
    if await repo.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=409,
            detail='Пользователь с таким username существует'
        )

    if await repo.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=409,
            detail='Пользователь с таким email существует'
        )

    data = await repo.create_user(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    return UserResponse(
        id = data.id,
        username = data.username,
        email = data.email,
        role = 'user'
    )


@router.get('/', response_model=list[UserResponse], summary='Получить список пользователей')
async def get_users(
        session: AsyncSession = Depends(get_async_session),
):
    repo = UserRepository(session)
    return await repo.get_all_users()


@router.get('/me', response_model=list[UserResponse], summary='Получить список пользователей')
async def get_users(
        session: AsyncSession = Depends(get_async_session),
        current_user: UserInDB = Depends(get_current_user)
):
    repo = UserRepository(session)
    return await repo.get_user_by_id(user_id=current_user.id)



#Подключение стороннего API


@router.get('/external-users/{user_id}')
async def get_external_user(user_id: int):
    url = f'https://jsonplaceholder.typicode.com/users/{user_id}'
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail='Ошибка внешнего API')
        return response.json()


@router.post('/create-external-post')
async def create_external_post(title: str, body: str):
    url = 'https://jsonplaceholder.typicode.com/posts/'
    payload = {'title': title, 'body': body}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
    return {'status_code': response.status_code, "response_data": response.json()}