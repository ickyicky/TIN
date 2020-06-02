import pytest
import string
import random
import json


@pytest.fixture
def username_generator(client):
    def generator():
        client.authorize()
        response = client.get("users")
        assert response.status_code == 200
        USERNAMES = {u["username"] for u in response.json()}

        while True:
            username = "".join(random.choice(string.ascii_letters) for i in range(10))
            if username not in USERNAMES:
                return username

    return generator


@pytest.fixture
def username(username_generator):
    return username_generator()


@pytest.fixture
def password_generator():
    def generator():
        password = "".join(random.choice(string.ascii_uppercase) for i in range(4))
        password += "".join(random.choice(string.ascii_lowercase) for i in range(4))
        password += "".join(random.choice(string.digits) for i in range(4))
        return password

    return generator


@pytest.fixture
def password(password_generator):
    return password_generator()


@pytest.fixture
def user_payload_generator(username, password):
    def generator(**kwargs):
        result = {
            "username": username,
            "password": password,
            "role": 1,
        }
        result.update(**kwargs)
        return result

    return generator


@pytest.fixture()
def user_payload(user_payload_generator):
    return user_payload_generator()


@pytest.fixture
def user_factory(client, user_payload_generator, username_generator):
    def generator(**kwargs):
        user_payload = user_payload_generator()
        user_payload.update(**kwargs)
        client.authorize()
        while True:
            result = client.post(
                "users", json.dumps(user_payload), headers=client.JSON_HEADER
            )
            if result.status_code == 200:
                break
            user_payload["username"] = username_generator()

    return generator
