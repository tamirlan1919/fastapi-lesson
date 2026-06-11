from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException, Query, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from motor.motor_asyncio import AsyncIOMotorCollection
from src.auth import get_current_user
from src.database import get_async_session, get_task_history_collection
from src.publisher import publish_export_task
from src.repositories.tasks_repo import TaskRepository
from src.repositories.task_history import TaskHistory
from src.schemas import TaskResponse, TaskCreate, TaskUpdate, TaskToDone, UserInDB
from src.services.task_rules import validate_task_business_rules
from redis.asyncio import Redis
from src.redis_client import get_redis
from src.services.cache_service import CacheService



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


@router.get('/with-history')
async def get_tasks_with_history(
        current_user: UserInDB = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
        history_col: AsyncIOMotorCollection = Depends(get_task_history_collection)
):
    repo = TaskRepository(session)
    tasks = await repo.get_all_tasks_for_user(owner_id=current_user.id)
    if not tasks:
        return []
    tasks_ids = [t.id for t in tasks]
    history =  TaskHistory(history_col)
    last_events = await history.get_last_events(tasks_ids)
    return [
        {
            'id': t.id,
            'title': t.title,
            'priority': t.priority,
            'is_done': t.is_done,
            'created_at': str(t.created_at),
            'last_event': last_events.get(t.id, 'created')

        } for t in tasks
    ]


@router.post('/', response_model=TaskResponse, status_code=201)
async def create_task(task: TaskCreate,
                      current_user: UserInDB = Depends(get_current_user),
                      session: AsyncSession = Depends(get_async_session),
                      history_col: AsyncIOMotorCollection = Depends(get_task_history_collection),
                      redis: Redis = Depends(get_redis)
                      ):
    repo = TaskRepository(session)
    created = await repo.create(task_data=task, owner_id=current_user.id)
    try:
        history =  TaskHistory(history_col)
        await history.log_cretated(
            task_id=created.id,
            user_id=current_user.id,
            snapshot={
                'title': created.title,
                'is_done': created.is_done,
                'deadline': str(created.deadline) if created.deadline else None
            }
        )
    except Exception as e:
        print(f'Warn task_history log failed: {e}')
    await CacheService(redis).invalidate_tasks(current_user.id)
    return created


@router.post('/export')
async def export_task(
        fmt: str = Query('csv'),
        current_user=Depends(get_current_user),

):
    await publish_export_task(
        user_id=current_user.id,
        fmt=fmt
    )
    return {
        'status': 'queued',
        'message': f'Экспорт в {fmt}',
        'user_id': current_user.id


    }


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




