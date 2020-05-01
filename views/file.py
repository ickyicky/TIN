from server.response import Statuses, HTTPResponse
import os


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
        with open(os.path.join("data", file_path), "rb") as f:
            f.seek(offset)
            content = f.read(lenght)
        return HTTPResponse(Statuses.OK, content)
    except:
        return HTTPResponse(Statuses.NOT_FOUND)


def FilePost(file_path, request):
    try:
        with open(os.path.join("data", file_path), "wb") as f:
            content = f.write(request.data)
        return HTTPResponse(Statuses.OK)
    except:
        return HTTPResponse(Statuses.NOT_FOUND)


def MakeDir(dir_path, request):
    try:
        os.makedirs(os.path.join("data", dir_path), exist_ok=True)
        return HTTPResponse(Statuses.OK)
    except:
        return HTTPResponse(Statuses.NOT_FOUND)


def ListDir(dir_path, request):
    try:
        content = os.listdir(os.path.join("data", dir_path))
        return HTTPResponse(Statuses.OK, str(content))
    except:
        return HTTPResponse(Statuses.NOT_FOUND)
