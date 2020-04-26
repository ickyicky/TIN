from server.response import Statuses, HTTPResponse
import os


def FileGet(file_path, data=None):
    try:
        with open(os.path.join("data", file_path), "rb") as f:
            content = f.read()
        return HTTPResponse(Statuses.OK, content)
    except:
        return HTTPResponse(Statuses.NOT_FOUND)


def FilePost(file_path, data):
    try:
        with open(os.path.join("data", file_path), "wb") as f:
            content = f.write(data)
        return HTTPResponse(Statuses.OK)
    except:
        return HTTPResponse(Statuses.NOT_FOUND)


def MakeDir(dir_path, data=None):
    try:
        os.makedirs(os.path.join("data", dir_path), exist_ok=True)
        return HTTPResponse(Statuses.OK)
    except:
        return HTTPResponse(Statuses.NOT_FOUND)


def ListDir(dir_path="", data=None):
    try:
        content = os.listdir(os.path.join("data", dir_path))
        return HTTPResponse(Statuses.OK, str(content))
    except:
        return HTTPResponse(Statuses.NOT_FOUND)
