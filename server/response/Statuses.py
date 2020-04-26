import enum


class Statuses(enum.Enum):
    NOT_FOUND = 404
    NOT_ALLOWED = 402
    OK = 200
    SERVER_ERROR = 500
