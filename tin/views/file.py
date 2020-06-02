from ..server.response import Statuses, HTTPResponse
from ..server.middleware.AuthGuardian import needs_authorization
from ..guardian import lock_path
import os
import json
import re
from datetime import datetime


@needs_authorization
@lock_path("file_path", lock_path.Method.read)
def FileGet(file_path, request):
    range_ = request.headers.get("Range")
    offset = 0
    lenght = None
    if range_:
        try:
            assert range_.startswith("bytes=")
            range_ = range_.replace("bytes=", "")
            offset, lenght = range_.split("-")
            if offset:
                offset = int(offset)
            if lenght:
                lenght = int(lenght) - offset + 1
        except:
            return HTTPResponse(Statuses.BAD_REQUEST)
    try:
        assert not file_path.startswith("/")
        assert lenght is None or lenght > 0
        file_path = os.path.join("/app/data", file_path)
        with open(file_path, "rb") as f:
            f.seek(offset)
            content = f.read(lenght)
        headers = {}
        status = Statuses.OK
        if range_:
            total_size = os.stat(file_path).st_size
            range_from = offset
            range_to = offset + lenght - 1 if lenght else total_size
            if range_to >= total_size:
                range_to = total_size - 1
            headers["Content-Range"] = f"bytes {range_from}-{range_to}/{total_size}"
            status = Statuses.PARTIAL_CONTENT

        return HTTPResponse(status, content, headers=headers)
    except FileNotFoundError:
        return HTTPResponse(Statuses.NOT_FOUND)
    except AssertionError:
        return HTTPResponse(Statuses.BAD_REQUEST)


@needs_authorization
@lock_path("file_path", lock_path.Method.write)
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
            assert range_to - range_from + 1 == len(request.data)
        except:
            return HTTPResponse(Statuses.BAD_REQUEST)

    try:
        assert not file_path.startswith("/")
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
    except AssertionError:
        return HTTPResponse(Statuses.BAD_REQUEST)


@needs_authorization
@lock_path("file_path", lock_path.Method.delete)
def FileDelete(file_path, request):
    try:
        assert not file_path.startswith("/")
        file_path = os.path.join("/app/data", file_path)
        os.remove(file_path)
        return HTTPResponse(Statuses.OK)
    except FileNotFoundError:
        return HTTPResponse(Statuses.NOT_FOUND)
    except IsADirectoryError:
        return HTTPResponse(Statuses.BAD_REQUEST)
    except AssertionError:
        return HTTPResponse(Statuses.BAD_REQUEST)


@needs_authorization
@lock_path("dir_path", lock_path.Method.write)
def MakeDir(dir_path, request):
    try:
        assert not dir_path.startswith("/")
        os.makedirs(os.path.join("/app/data", dir_path), exist_ok=True)
        return HTTPResponse(Statuses.OK)
    except FileNotFoundError:
        return HTTPResponse(Statuses.NOT_FOUND)
    except AssertionError:
        return HTTPResponse(Statuses.BAD_REQUEST)


@needs_authorization
@lock_path("dir_path", lock_path.Method.read)
def ListDir(dir_path="", request=None, info="False"):
    if info.lower() in ("1", "yes", "true", "t"):
        info = True
    elif info.lower() in ("0", "no", "false", "f"):
        info = False
    else:
        return HTTPResponse(Statuses.BAD_REQUEST)

    try:
        assert not dir_path.startswith("/")
        dir_path = os.path.join("/app/data", dir_path)

        if info:
            content = []
            for item in os.listdir(dir_path):
                file_path = os.path.join(dir_path, item)
                content.append(
                    {
                        "name": item,
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
                )
        else:
            content = os.listdir(dir_path)

        return HTTPResponse(
            Statuses.OK,
            json.dumps(content),
            headers={"Content-Type": "applicaion/json"},
        )
    except (FileNotFoundError, NotADirectoryError):
        return HTTPResponse(Statuses.NOT_FOUND)
    except AssertionError:
        return HTTPResponse(Statuses.BAD_REQUEST)


@needs_authorization
@lock_path("dir_path", lock_path.Method.delete)
def DeleteDir(dir_path, request, recursive="False"):
    if recursive.lower() in ("1", "yes", "true", "t"):
        recursive = True
    elif recursive.lower() in ("0", "no", "false", "f"):
        recursive = False
    else:
        return HTTPResponse(Statuses.BAD_REQUEST)

    try:
        assert not dir_path.startswith("/")
        dir_path = os.path.join("/app/data", dir_path)
        if recursive:
            for root, dirs, files in os.walk(dir_path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
        os.rmdir(dir_path)
        return HTTPResponse(Statuses.OK)
    except FileNotFoundError:
        return HTTPResponse(Statuses.NOT_FOUND)
    except (AssertionError, NotADirectoryError, OSError):
        return HTTPResponse(Statuses.BAD_REQUEST)
