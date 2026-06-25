from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import Task
from src.schemas import TaskCreate, TaskUpdate
from fastapi import HTTPException, status
from typing import List, Optional


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, task_data: TaskCreate, owner_id:  int) -> Task:
        task = Task(
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            is_done=task_data.is_done,
            owner_id=owner_id
        )
        try:
            self.session.add(task)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=500,
                detail='Ошибка создания задачи'
            )

        await self.session.refresh(task)
        return task

    async def get_all_tasks_for_user(self,
                                     owner_id: int,
                                     is_done: Optional[bool] = None,
                                     priority: Optional[int] = None,
                                     limit: int = 10,
                                     offset: int = 0) -> List[Task]:
        stmt = select(Task).where(Task.owner_id == owner_id)
        if is_done is not None:
            stmt = stmt.where(Task.is_done == is_done)
        if priority is not None:
            stmt = stmt.where(Task.priority  == priority)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self,
                        task_id: int,
                        owner_id: int) -> Task | None:
        stmt = select(Task).where(
            Task.id == task_id,
            Task.owner_id == owner_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self,
                     task_id: int,
                     owner_id: int,
                     data: TaskUpdate) -> Task | None:
        task = await self.get_by_id(task_id=task_id, owner_id=owner_id)
        if not task:
            return None
        update_fields = data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(task, field, value)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete(self,
                     task_id: int,
                     owner_id: int) -> bool:
        task = await self.get_by_id(task_id=task_id, owner_id=owner_id)
        if not task:
            return False
        await self.session.delete(task)
        await self.session.commit()
        return True




