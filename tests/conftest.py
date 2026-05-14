import pytest
from fastapi.testclient import TestClient
from src.auth import hash_password
from src.main import app
from src.repositories.tasks_repo import reset_tasks_db
from src.repositories.users_repo import reset_users_db, seed_admin


@pytest.fixture(autouse=True)
def reset_state():
    reset_users_db()
    reset_tasks_db()

    seed_admin(hashed_password=hash_password('admin123'))

    yield

    reset_users_db()
    reset_tasks_db()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def user_payload():
    return {
        'username': 'alice',
        'email': 'alice@inbox.com',
        'password': 'strongpassword123'
    }


@pytest.fixture
def second_user_payload():
    return {
        'username': 'bob',
        'email': 'bob@inbox.com',
        'password': 'strongpassword123'
    }


@pytest.fixture
def user_token(client: TestClient, user_payload):
    client.post('/users/register/', json=user_payload)

    response = client.post(
        'auth/login',
        data={
            'username': user_payload['username'],
            'password': user_payload['password']
        }
    )
    return response.json()['access_token']


@pytest.fixture
def seocnd_user_token(client: TestClient, second_user_payload):
    client.post('/users/register/', json=second_user_payload)

    response = client.post(
        'auth/login',
        data={
            'username': second_user_payload['username'],
            'password': second_user_payload['password']
        }
    )
    return response.json()['access_token']


@pytest.fixture
def admin_token(client: TestClient):
    response = client.post(
        'auth/login',
        data={
            'username': 'admin',
            'password': 'admin123'
        }
    )
    return response.json()['access_token']
