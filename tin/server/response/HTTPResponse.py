from ..headers.HTTPHeaders import HTTPHeaders
import logging

log = logging.getLogger(__name__)


class HTTPResponse:
    def __init__(self, status, data=None, message=None, headers={}):
        data = data or message
        self.status = status
        if isinstance(data, str):
            data = data.encode()
        self.data = data

        self.headers = HTTPHeaders(headers)

    def close_connection(self):
        return self.headers.get("Connection") == "close"

    def timeout(self):
        if self.headers.get("Connection") == "close":
            return None

        try:
            return int(self.headers.get("Keep-Alive").split(", ")[0].split("=")[1])
        except:
            return None

    def encode(self):
        content = f"HTTP/1.1 {self.status.value} {self.status.name}\r\n".encode()

        if self.headers:
            content += self.headers.encode()

        while not content.endswith(b"\r\n\r\n"):
            content += b"\r\n"

        if self.data:
            content += self.data
        return content
