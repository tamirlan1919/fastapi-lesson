def test_create_user(client, user_payload):
    response = client.post('/users/register', json=user_payload)
    assert response.status_code == 201


def test_get_users_list(client, admin_token, user_payload):
    client.post('/users/register/', json=user_payload)
    response = client.get('/users', headers={
        'Authorization': f'Bearer {admin_token}'
    })
    assert response.status_code == 200
    assert isinstance(response.json(), list)

