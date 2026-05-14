def test_create_task(client, admin_token, user_token):
    client.post(
        '/tasks',
        headers={'Authorization': f'Bearer {user_token}'},
        json={
            'title': 'Помыть машину',
            'priority': 2
        }
    )
    client.post(
        '/tasks',
        headers={'Authorization': f'Bearer {user_token}'},
        json={
            'title': 'Поиграть в FIFA',
            'priority': 4
        }
    )

    response = client.get(
        '/tasks',
        headers={'Authorization': f'Bearer {admin_token}'},
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]['title'] == 'Помыть машину'


def test_create_task_no_valid(client, admin_token, user_token):
    response = client.post(
        '/tasks',
        headers={'Authorization': f'Bearer {user_token}'},
        json={
            "title": "Помыть машину",
            "priority": "fsdfsdf"
        }
    )
    assert response.status_code == 422
