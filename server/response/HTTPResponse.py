from ..headers.HTTPHeaders import HTTPHeaders


class HTTPResponse:
    def __init__(self, status, data=None, headers={}):
        self.status = status
        self.data = data

        if "Connection" not in headers:
            headers.update({"Connection": "keep-alive"})

        if headers["Connection"] == "keep-alive" and "Keep-Alive" not in headers:
            headers.update({"Keep-Alive": "timeout=5, max=1000"})

        if "Content-Length" not in headers:
            headers.update({"Content-Length": len(data)})

        if "Content-Type" not in headers:
            headers.update({"Content-Type": "application/octet-stream"})

        self.headers = HTTPHeaders(headers)

    def close_connection(self):
        return self.headers.get("Connection") == "close"

    def timeout(self):
        if self.headers.get("Connection") == "close":
            return None

        return int(self.headers.get("Keep-Alive").split(", ")[0].split("=")[1])

    def encode(self):
        content = f"HTTP/1.1 {self.status.value} {self.status.name}\r\n".encode()

        if self.headers:
            content += self.headers.encode()

        if isinstance(self.data, str):
            self.data = self.data.encode()

        while not content.endswith(b"\r\n\r\n"):
            content += b"\r\n"

        if self.data:
            content += self.data
        return content
