class HTTPResponse:
    def __init__(self, status, data=None, headers=None):
        self.status = status
        self.data = data

    def encode(self):
        content = f"HTTP/1.1 {self.status.value} {self.status.name}\n\n".encode()

        if isinstance(self.data, str):
            self.data = self.data.encode()

        if self.data:
            content += self.data
        return content
