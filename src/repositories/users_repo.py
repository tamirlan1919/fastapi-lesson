from src.schemas import UserInDB

users_db: dict[str, UserInDB] = {}
next_user_id = 0


def reset_users_db():
    """Для тестов"""
    global next_user_id
    users_db.clear()
    next_user_id = 0


def seed_admin(hashed_password: str) -> None:
    global next_user_id
    if 'admin' in users_db:
        return

    users_db['admin'] = UserInDB(
        id = 1,
        username='admin',
        email='admin@inbox.com',
        hashed_password=hashed_password,
        role='admin'
    )
    next_user_id += max(next_user_id, 1)


def get_user_by_username(username: str) -> UserInDB | None:
    return users_db.get(username)


def get_user_by_email(email: str) -> UserInDB | None:
    for user in users_db.values():
        if user.email == email:
            return user
    return None


def list_users():
    return list(users_db.values())


def create_user(
        username: str,
        email: str,
        hashed_password: str,
        role: str = 'role'
) -> UserInDB:
    global next_user_id

    next_user_id += 1

    user = UserInDB(
        id=next_user_id,
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=role
    )

    users_db[username] = user

    return user