import enum


class Statuses(enum.Enum):
    BAD_REQUEST = 400
    NOT_FOUND = 404
    NOT_ALLOWED = 405
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    OK = 200
    PARTIAL_CONTENT = 206
    SERVER_ERROR = 500
