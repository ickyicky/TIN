from ..handler import HTTPException
from ..response import Statuses
import logging

log = logging.getLogger(__name__)


def needs_authorization(func):
    def decorated(*args, request, **kwargs):
        if request.user is None:
            raise HTTPException(status=Statuses.UNAUTHORIZED, message="Unauthorized")
        return func(*args, request=request, **kwargs)

    return decorated


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
