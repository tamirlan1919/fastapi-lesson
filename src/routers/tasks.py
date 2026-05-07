from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException, Query, Response, Depends

from src.auth import get_current_user
from src.schemas import TaskResponse, TaskCreate, TaskUpdate, TaskToDone, UserInDB

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)

tasks_db: dict[int, dict] = {}
next_id: int = 1




@router.get('/', response_model=List[TaskResponse])
async def get_tasks(
        is_done: bool | None = Query(None, description="Filter tasks by completion status"),
        priority: int | None = Query(None, ge=1, le=5, description="Filter tasks by priority (1-5)"),
        limit: int = Query(10, ge=1, le=100, description="Limit the number of tasks returned"),
        offset: int = Query(0, ge=0, description="Number of tasks to skip before starting to collect the result set")
):
    tasks = list(tasks_db.values())
    if is_done is not None:
        tasks = [task for task in tasks if task['is_done'] == is_done]
    if priority is not None:
        tasks = [task for task in tasks if task['priority'] == priority]

    return tasks[offset:offset + limit]


@router.get('/my', response_model=TaskResponse, summary='Получить мои задачи')
async def get_my_tasks(current_user: UserInDB =  Depends(get_current_user)):
    tasks = [
        task for task in tasks_db.values() if task['owner_username'] == current_user.username
    ]

    return tasks


@router.post('/', response_model=TaskResponse, status_code=201)
async def create_task(task: TaskCreate, current_user: UserInDB = Depends(get_current_user)):


    global next_id
    now = datetime.now(timezone.utc)
    task_data = task.model_dump()
    task_data['id'] = next_id
    task_data['userId'] = current_user.id
    task_data['created_at'] = now
    task_data['updated_at'] = now
    tasks_db[next_id] = task_data
    next_id += 1
    return task_data


@router.put('/{task_id}', response_model=TaskResponse)
async def update_task(task_id: int, task: TaskUpdate):
    existing_task = tasks_db.get(task_id)
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")

    updated_data = task.model_dump(exclude_unset=True)
    existing_task.update(updated_data)
    existing_task['updated_at'] = datetime.now(timezone.utc)
    return existing_task


@router.delete('/{task_id}', status_code=204)
async def delete_task(task_id: int):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks_db[task_id]
    return Response(status_code=204)

@router.get('/{task_id}', response_model=TaskResponse)
async def get_task(task_id: int):
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task



@router.patch('/{task_id}/complete/', response_model=TaskResponse)
async def change_task_to_complete(task_id: int, task: TaskToDone):
    existing_task = tasks_db.get(task_id)
    if not existing_task:
        raise HTTPException(status_code=404, detail='Задача не найдена')

    update_data = task.model_dump(exclude_unset=True)
    if 'is_done' not in update_data:
        update_data['is_done'] = True

    existing_task.update(update_data)
    existing_task['updated_at'] = datetime.now(timezone.utc)
    return existing_task
