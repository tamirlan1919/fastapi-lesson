tasks_db: dict[int, dict] = {}
next_task_id = 0


def reset_tasks_db():
    """Для тестов"""
    global next_task_id
    tasks_db.clear()
    next_task_id = 0


def list_tasks() -> list[dict] | None:
    return list(tasks_db.values())


def get_task_by_id(task_id: int) -> dict | None:
    return tasks_db.get(task_id)


def repo_create_task(task_data: dict) -> dict:
    global next_task_id

    next_task_id += 1
    data_to_save = task_data.copy()
    data_to_save['id'] = next_task_id
    tasks_db[next_task_id] = data_to_save
    print(data_to_save)
    return data_to_save


def update_task(taks_id: int, updated_data: dict) -> dict | None:
    task = tasks_db.get(taks_id)
    if task is None:
        return None
    task.update(updated_data)
    return task


def delete_task(task_id: int) -> bool:
    if task_id not in tasks_db:
        return False
    del tasks_db[task_id]
    return True