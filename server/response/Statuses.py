import enum


class Statuses(enum.Enum):
    BAD_REQUEST = 400
    NOT_FOUND = 404
    NOT_ALLOWED = 405
    OK = 200
    SERVER_ERROR = 500
