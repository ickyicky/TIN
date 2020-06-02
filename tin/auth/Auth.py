import datetime
import jwt
import logging
import traceback
import random
import string

log = logging.getLogger(__name__)


class Authorization:
    def __init__(self, user_model, secret):
        self.user_model = user_model
        self.secret = secret

    def authorize_password(self, request, username, password):
        try:
            user = (
                request.dbssn.query(self.user_model)
                .filter_by(username=username)
                .first()
            )
            assert user.password_check(password)
            return user
        except:
            pass

    def authorize(self, request, token):
        try:
            decoded = jwt.decode(token, self.secret, algorithms=["HS256"],)
            log.debug(decoded)
            claim = datetime.datetime.fromtimestamp(float(decoded["expires"]))
            log.debug(claim)
            assert claim > datetime.datetime.utcnow()
            user = (
                request.dbssn.query(self.user_model)
                .filter(self.user_model.id == int(decoded["user_id"]))
                .first()
            )
            return user
        except Exception as e:
            log.debug(traceback.format_exc())
            log.debug(repr(e))
            return

    def token_for_user(self, request, user):
        expires = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        payload = {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "user_id": user.id,
            "expires": expires.timestamp(),
            "hash": "".join(random.choice(string.ascii_letters) for i in range(30)),
        }
        encoded_jwt = jwt.encode(payload, self.secret, algorithm="HS256")
        return encoded_jwt.decode()
