from ..server.response import Statuses, HTTPResponse
import json


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
