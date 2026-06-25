import httpx
import os

API_URL = os.getenv('API_URL', 'http://tracker-api:8000')


async def login(username: str, password: str) -> str | None:
    """
    /auth/login
    :param username:
    :param password:
    :return:
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f'{API_URL}/auth/login',
            data={
                'username': username,
                'password': password
            }
        )
        if response.status_code == 200:
            return response.json()['access_token']

        return None


async def get_tasks(token: str, limit: int = 10) -> list[dict]:
    """
    /tasks
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'{API_URL}/tasks/',
            headers={'Authorization': f'Bearer {token}'},
            params={'limit': limit}
        )
        if response.status_code == 401:
            return []
        response.raise_for_status()
        return response.json()


async def create_task(token: str, title: str, priority: int = 1) -> dict | None:
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            f'{API_URL}/tasks/',
            json={'title': title, 'priority': priority},
            headers={'Authorization': f'Bearer {token}'}
        )
        if response.status_code == 201:
            return response.json()
        return None



# async def complete_task(token: str, task_id: int) -> bool:
#     async with httpx.AsyncClient() as client:
#         response = client.patch(
#             f'{API_URL}/tasks/{task_id}/done'
#         )