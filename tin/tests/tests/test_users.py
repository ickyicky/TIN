import json
import pytest
import random


@pytest.mark.parametrize(
    "role,expected_status", [(1, 403), (2, 200),],
)
def test_user_get_permissions(
    client, role, expected_status, user_factory, user_payload
):
    user_payload["role"] = role
    user_factory(**user_payload)
    client.authorize(user_payload["username"], user_payload["password"])

    result = client.get("users")
    assert result.status_code == expected_status


def test_uset_get_limit_offset(client, user_factory):
    for _ in range(10):
        user_factory()

    result = client.get("users")
    assert result.status_code == 200
    parsed = result.json()
    total_count = len(parsed)

    offset = int(total_count * 0.2)
    limit = int(total_count * 0.5)
    reference_data = parsed[offset : offset + limit]

    result = client.get(f"users?limit={limit}&offset={offset}")
    assert result.status_code == 200
    parsed = result.json()
    assert len(parsed) == limit
    assert reference_data == parsed


@pytest.mark.parametrize(
    "role,expected_status", [(1, (403,)), (2, (200, 400)),],
)
def test_user_create_permissions(
    client, role, expected_status, user_factory, user_payload_generator
):
    user_payload = user_payload_generator(role=role)
    user_factory(**user_payload)
    client.authorize(user_payload["username"], user_payload["password"])

    result = client.post(
        "users", json.dumps(user_payload_generator()), headers=client.JSON_HEADER
    )
    assert result.status_code in expected_status


def test_user_modify(client):
    client.authorize()
    result = client.get("users")

    assert result.status_code == 200
    mapper = {u["id"]: u for u in result.json()}

    id_ = random.choice(list(mapper.keys()))
    payload = {"first_name": "GRZESIEK"}
    reference_data = mapper[id_]
    reference_data.update(**payload)

    result = client.patch(
        f"users/{id_}", json.dumps(payload), headers=client.JSON_HEADER
    )
    assert result.status_code == 200
    result = client.get("users")
    assert result.status_code == 200
    user_payload = {u["id"]: u for u in result.json()}[id_]
    assert user_payload == reference_data


def test_user_delete(client):
    client.authorize()
    result = client.get("users")

    assert result.status_code == 200
    mapper = {u["id"]: u for u in result.json()}

    id_ = random.choice(list(mapper.keys()))
    reference_data = mapper[id_]

    result = client.delete(f"users/{id_}")
    assert result.status_code == 200
    result = client.get("users")
    assert result.status_code == 200
    assert reference_data not in result.json()


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
