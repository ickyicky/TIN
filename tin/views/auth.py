from ..server.response import Statuses, HTTPResponse
from ..server.middleware.AuthGuardian import needs_authorization
from ..serializers.user import UserPasswordChangeSerializer
import json

import logging

log = logging.getLogger(__name__)


def authorize(request):
    try:
        data = json.loads(request.data)
        user = request.auth.authorize_password(
            request, username=data["username"], password=data["password"]
        )
        assert user is not None
        return HTTPResponse(
            Statuses.OK,
            headers={
                "Authorization": f"BEARER {request.auth.token_for_user(request, user)}"
            },
        )
    except:
        return HTTPResponse(Statuses.BAD_REQUEST, message="Bad credentials")


@needs_authorization
def prolong_session(request):
    return HTTPResponse(
        Statuses.OK,
        headers={
            "Authorization": f"BEARER {request.auth.token_for_user(request, request.user)}"
        },
    )


@needs_authorization
def change_password(request):
    try:
        data = json.loads(request.data)
    except:
        return HTTPResponse(Statuses.BAD_REQUEST)

    data["id"] = request.user.id
    UserPasswordChangeSerializer.modify(data, request)
    return HTTPResponse(Statuses.OK)
