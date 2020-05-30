from ..server.response import Statuses, HTTPResponse
from ..server.middleware.AuthGuardian import needs_authorization
import os
import json
import re
from datetime import datetime


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
            lenght = int(lenght) - offset
    try:
        file_path = os.path.join("/app/data", file_path)
        with open(file_path, "rb") as f:
            f.seek(offset)
            content = f.read(lenght)
        headers = {}
        status = Statuses.OK
        if offset:
            total_size = os.stat(file_path).st_size
            range_from = offset
            range_to = lenght or total_size
            headers["Content-Range"] = f"bytes {range_from}-{range_to}/{total_size}"
            status = Statuses.PARTIAL_CONTENT

        return HTTPResponse(status, content, headers=headers)
    except FileNotFoundError:
        return HTTPResponse(Statuses.NOT_FOUND)


@needs_authorization
def FilePost(file_path, request):
    range_ = request.headers.get("Content-Range")
    offset = 0
    total_bytes = None
    if range_:
        try:
            values = re.findall(r"^(\w+) (\d+)-(\d+)/(\d+)", range_)[0]
            assert values[0] == "bytes"
            range_from = int(values[1])
            range_to = int(values[2])
            total_bytes = int(values[3])
            assert range_to >= range_from
            assert range_to < total_bytes
            offset = range_from
        except:
            return HTTPResponse(Statuses.BAD_REQUEST)

    try:
        try:
            with open(os.path.join("/app/data", file_path), "r+b") as f:
                f.seek(offset)
                f.write(request.data)
                if total_bytes:
                    f.seek(total_bytes)
                f.truncate()
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
def ListDir(dir_path="", request=None):
    try:
        content = {}
        dir_path = os.path.join("/app/data", dir_path)
        for item in os.listdir(dir_path):
            file_path = os.path.join(dir_path, item)
            content[item] = {
                "type": "file" if os.path.isfile(file_path) else "directory",
                "size": os.path.getsize(file_path),
                "atime": datetime.fromtimestamp(
                    os.path.getatime(file_path)
                ).isoformat(),
                "ctime": datetime.fromtimestamp(
                    os.path.getctime(file_path)
                ).isoformat(),
                "mtime": datetime.fromtimestamp(
                    os.path.getmtime(file_path)
                ).isoformat(),
            }
            return HTTPResponse(
                Statuses.OK,
                json.dumps(content),
                headers={"Content-Type": "applicaion/json"},
            )
    except FileNotFoundError as e:
        raise e
        return HTTPResponse(Statuses.NOT_FOUND)
