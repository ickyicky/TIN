from ..handler import HTTPException
from ..response import Statuses
import logging
import functools

log = logging.getLogger(__name__)


def needs_authorization(func):
    @functools.wraps(func)
    def decorated(*args, request, **kwargs):
        if request.user is None:
            raise HTTPException(status=Statuses.UNAUTHORIZED, message="Unauthorized")
        return func(*args, request=request, **kwargs)

    return decorated


def needs_role(role):
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, request, **kwargs):
            if request.user is None:
                raise HTTPException(
                    status=Statuses.UNAUTHORIZED, message="Unauthorized"
                )

            if request.user.role != role:
                raise HTTPException(
                    status=Statuses.NOT_ALLOWED,
                    message=f"Insufisient priviliges a{request.user.role}a{role}a",
                )
            return func(*args, request=request, **kwargs)

        return wrapper

    return actual_decorator


class AuthGuardian:
    def __init__(self, auth):
        self.auth = auth

    def process_request(self, request):
        request.auth = self.auth
        try:
            token = request.headers.get("Authorization")
            token = token.replace("BEARER ", "")
            user = request.auth.authorize(request, token)
        except:
            user = None

        request.user = user

    def process_response(self, response, request):
        token = request.headers.get("Authorization")
        if token:
            response.headers.update(Authorization=token)
