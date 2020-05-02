from ..server.response import Statuses, HTTPResponse
from ..server.middleware.AuthGuardian import needs_authorization
import os


@needs_authorization
def FileGet(file_path, request):
    range_ = request.headers.get("Range")
    offset = 0
    lenght = None
    if range_:
        offset, lenght = range_.split("-")
        if offset:
            offset = int(offset)
        if lenght:
            lenght = int(lenght)
    try:
        with open(os.path.join("/app/data", file_path), "rb") as f:
            f.seek(offset)
            content = f.read(lenght)
        return HTTPResponse(Statuses.OK, content)
    except FileNotFoundError:
        return HTTPResponse(Statuses.NOT_FOUND)


@needs_authorization
def FilePost(file_path, request):
    range_ = request.headers.get("Range")
    offset = 0
    lenght = None
    if range_:
        offset, lenght = range_.split("-")
        if offset:
            offset = int(offset)
        if lenght:
            lenght = int(lenght)

    try:
        try:
            with open(os.path.join("/app/data", file_path), "r+b") as f:
                f.seek(offset)
                f.write(request.data)
        except FileNotFoundError:
            with open(os.path.join("/app/data", file_path), "wb") as f:
                f.write(request.data)

        return HTTPResponse(Statuses.OK)
    except FileNotFoundError:
        return HTTPResponse(Statuses.NOT_FOUND)


@needs_authorization
def MakeDir(dir_path, request):
    try:
        os.makedirs(os.path.join("/app/data", dir_path), exist_ok=True)
        return HTTPResponse(Statuses.OK)
    except FileNotFoundError:
        return HTTPResponse(Statuses.NOT_FOUND)


@needs_authorization
def ListDir(dir_path, request):
    try:
        content = os.listdir(os.path.join("/app/data", dir_path))
        return HTTPResponse(Statuses.OK, str(content))
    except FileNotFoundError:
        return HTTPResponse(Statuses.NOT_FOUND)
