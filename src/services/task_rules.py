from fastapi import HTTPException, status


def validate_task_business_rules(task_data: dict) -> None:
    if task_data.get('priority') == 5 and task_data.get('deadline') is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Для задачи с приоритетом 5 нужно указать дедлайн'
        )

