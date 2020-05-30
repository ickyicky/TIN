from ..server.response import Statuses, HTTPResponse
import json
from ..domain import User


def validate_string(string, name):
    assert len(string) <= 100, f"{name} too long"
    assert len(string) >= 10, f"{name} too short"
    assert all(
        (x.isascii() for x in string)
    ), f"{name} must contain only ascii characters"


def assert_password_is_secure(password):
    validate_string(password, "password")
    assert any((x.isdigit() for x in password)), "password must contain 1 digit"
    assert any(
        (x.isalpha() for x in password)
    ), "password must contain at least one letter"


def create(request):
    try:
        data = json.loads(request.data)
    except:
        return HTTPResponse(Statuses.BAD_REQUEST, "Invalid payload")

    try:
        assert_password_is_secure(data["password"])
    except AssertionError as e:
        return HTTPResponse(Statuses.BAD_REQUEST, e.args[0])
    except KeyError as e:
        return HTTPResponse(Statuses.BAD_REQUEST, f"Missing key: {e.args[0]}")
