from . import base
from .. import domain
import logging
from ..server.handler.HTTPExceptions import HTTPException
from ..server.response import Statuses

log = logging.getLogger(__name__)

USERNAME_REGEX = r"^[A-Za-z0-9\_]+$"


def password_is_secure(password):
    assert any((x.isdigit() for x in password)), "password must contain 1 digit"
    assert any(
        (x.isalpha() for x in password)
    ), "password must contain at least one letter"
    return password


class UserSerializer(base.ModelSerializer):
    id = base.IntegerSerializer()
    username = base.StringSerializer(
        min_length=8, max_length=100, regex=USERNAME_REGEX, unique=True
    )
    first_name = base.StringSerializer(min_length=1, max_length=100)
    last_name = base.StringSerializer(min_length=1, max_length=100)
    role = base.IntegerSerializer(min_value=1, max_value=2)

    class Meta:
        fields = ("id", "username", "first_name", "last_name", "role")
        model = domain.User


class UserWriteSerializer(base.ModelSerializer):
    password = base.StringSerializer(
        min_length=8, max_length=100, method=password_is_secure
    )
    username = base.StringSerializer(
        min_length=8, max_length=100, regex=USERNAME_REGEX, unique=True
    )
    first_name = base.StringSerializer(min_length=1, max_length=100)
    last_name = base.StringSerializer(min_length=1, max_length=100)
    role = base.IntegerSerializer(min_value=1, max_value=2)

    class Meta:
        fields = ("username", "password", "first_name", "last_name", "role")
        model = domain.User

    @classmethod
    def additional_modifications(cls, data, request, obj):
        if data.get("password"):
            obj.password_set(data["password"])


class UserPasswordChangeSerializer(base.ModelSerializer):
    old_password = base.StringSerializer(min_length=8, max_length=100, required=True)
    new_password = base.StringSerializer(
        min_length=8, max_length=100, method=password_is_secure, required=True
    )

    class Meta:
        fields = ("old_password", "new_password")
        model = domain.User

    @classmethod
    def additional_modifications(cls, data, request, obj):
        if not obj.password_check(data["old_password"]):
            raise HTTPException(Statuses.BAD_REQUEST, "Invalid old password")

        obj.password_set(data["new_password"])
