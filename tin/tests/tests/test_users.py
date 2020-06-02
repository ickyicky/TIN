import json


def test_user_prolong_session(client):
    client.authorize()

    result = client.post("prolong-session")
    assert result.status_code == 200
    assert result.headers["Authorization"] != client.session.headers["Authorization"]


def test_create_user_change_password(client):
    client.authorize()

    username = "testusername"
    password = "ExamplePassword123"

    user_payload = {
        "username": username,
        "password": password,
        "role": 1,
    }

    result = client.post("users", json.dumps(user_payload), headers=client.JSON_HEADER)
    assert result.status_code == 200

    result = client.authorize(username=username, password=password)

    payload = {
        "old_password": password,
        "new_password": password + "4",
    }
    result = client.post(
        "change-password", json.dumps(payload), headers=client.JSON_HEADER
    )
    assert result.status_code == 200

    try:
        result = client.authorize(username=username, password=password)
        raise Exception()
    except AssertionError:
        pass
