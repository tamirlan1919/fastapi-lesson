from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException, Query, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_user
from src.database import get_async_session
from src.repositories.tasks_repo import TaskRepository
from src.schemas import TaskResponse, TaskCreate, TaskUpdate, TaskToDone, UserInDB
from src.services.task_rules import validate_task_business_rules
from redis.asyncio import Redis
from src.redis_client import get_redis
from src.services.cachce_service import CacheService


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


@router.get('/', response_model=List[TaskResponse])
async def get_tasks(
        is_done: bool | None = Query(None, description="Filter tasks by completion status"),
        priority: int | None = Query(None, ge=1, le=5, description="Filter tasks by priority (1-5)"),
        limit: int = Query(10, ge=1, le=100, description="Limit the number of tasks returned"),
        offset: int = Query(0, ge=0, description="Number of tasks to skip before starting to collect the result set"),
        current_user: UserInDB = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
        redis: Redis = Depends(get_redis)

):
    cahce = CacheService(redis)
    cached_tasks = await cahce.get_tasks(current_user.id)
    if cached_tasks is not None:
        return cached_tasks

    repo = TaskRepository(session)
    tasks = await repo.get_all_tasks_for_user(owner_id=current_user.id,
                                              is_done=is_done,
                                              priority=priority,
                                              limit=limit
                                              ,offset=offset)
    await cahce.set_tasks(user_id=current_user.id, tasks=tasks)
    return tasks


@router.post('/', response_model=TaskResponse, status_code=201)
async def create_task(task: TaskCreate,
                      current_user: UserInDB = Depends(get_current_user),
                      session: AsyncSession = Depends(get_async_session)
                      ):
    repo = TaskRepository(session)

    return await repo.create(task_data=task, owner_id=current_user.id)


@router.get('/{task_id}', response_model=TaskResponse)
async def get_task(task_id: int,
                   current_user: UserInDB = Depends(get_current_user),
                   session: AsyncSession = Depends(get_async_session)
                   ):
    repo = TaskRepository(session)
    return await repo.get_by_id(task_id=task_id, owner_id=current_user.id)


@router.put('/{task_id}', response_model=TaskResponse)
async def update_task(task_id: int,
                      task: TaskUpdate,
                      current_user: UserInDB = Depends(get_current_user),
                      session: AsyncSession = Depends(get_async_session)
                      ):
    repo = TaskRepository(session)
    updated = await repo.update(task_id=task_id, owner_id=current_user.id, data=task)
    if not updated:
        raise HTTPException(status_code=404, detail='Task not found')
    return updated


@router.delete('/{task_id}', status_code=204)
async def delete_task(task_id: int,
                      current_user: UserInDB = Depends(get_current_user),
                      session: AsyncSession = Depends(get_async_session)):
    repo = TaskRepository(session)
    deleted = await repo.delete(task_id=task_id, owner_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail='Task not found')
    return Response(status_code=204)




