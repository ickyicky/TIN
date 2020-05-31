from ..server.response import Statuses, HTTPResponse
from ..server.middleware.AuthGuardian import needs_role
from ..serializers.user import UserSerializer, UserWriteSerializer
import json
from ..domain import User


@needs_role(User.Role.admin.value)
def get(request, limit=None, offset=None):
    try:
        if limit:
            limit = int(limit)
        if offset:
            offset = int(offset)
    except:
        return HTTPResponse(Statuses.BAD_REQUEST, "Invalid limit or offset")

    users = request.dbssn.query(User).order_by(User.id).all()
    content = []

    for user in users:
        content.append(UserSerializer.parse(user))

    return HTTPResponse(
        Statuses.OK, json.dumps(content), headers={"Content-Type": "applicaion/json"},
    )


@needs_role(User.Role.admin.value)
def create(request):
    try:
        data = json.loads(request.data)
    except:
        return HTTPResponse(Statuses.BAD_REQUEST, "Invalid payload")

    UserWriteSerializer.create(data, request)
    return HTTPResponse(Statuses.OK)


@needs_role(User.Role.admin.value)
def modify(request, user_id):
    try:
        data = json.loads(request.data)
        data["id"] = int(user_id)
    except:
        return HTTPResponse(Statuses.BAD_REQUEST, "Invalid payload")

    UserWriteSerializer.modify(data, request)
    return HTTPResponse(Statuses.OK)


@needs_role(User.Role.admin.value)
def delete(request, user_id):
    try:
        user_id = int(user_id)
    except:
        return HTTPResponse(Statuses.BAD_REQUEST, "Invalid payload")

    user = request.dbssn.query(User).filter_by(id=user_id).first()
    if user is None:
        return HTTPResponse(Statuses.NOT_FOUND)

    request.dbssn.delete(user)
    request.dbssn.commit()

    return HTTPResponse(Statuses.OK)
