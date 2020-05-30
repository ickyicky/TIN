import hashlib
import random
import string
import enum

from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    MetaData,
)
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
DBObject = declarative_base(metadata=metadata)


class PasswordAuthMixIn:
    def password_check(self, password):
        if not password:
            return False
        if not self.htpasswd:
            return False
        return (
            hashlib.sha1((self.htpasswd[:16] + password).encode("UTF-8")).hexdigest()
            == self.htpasswd[16:].lower()
        )

    @classmethod
    def password_hash(cls, password):
        rand = random.SystemRandom()
        salt = "".join(
            rand.choice(string.ascii_letters + string.digits) for i in range(16)
        )
        return salt + hashlib.sha1((salt + password).encode("UTF-8")).hexdigest()

    def password_set(self, password):
        self.htpasswd = self.password_hash(password)


class User(DBObject, PasswordAuthMixIn):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    htpasswd = Column(Unicode(100))
    username = Column(Unicode(100))
    first_name = Column(Unicode(100))
    last_name = Column(Unicode(100))
    role = Column(Integer)

    class Role(enum.Enum):
        user = 1
        admin = 2
