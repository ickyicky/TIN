import datetime


class HTTPHeaders:
    DATE_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"
    SERVER = "PythonTIN/0.1"

    def __init__(self, headers={}, **kwargs):
        self._headers = {
            "Date": datetime.datetime.utcnow().strftime(self.DATE_FORMAT),
            "Server": self.SERVER,
        }
        self.update(headers, **kwargs)

    def encode(self):
        result = "\r\n".join(f"{key}: {val}" for key, val in self._headers.items())
        return result.encode()

    def update(self, headers={}, **kwargs):
        for k, v in headers.items():
            self._headers.update({k.title(): v})

        for k, v in kwargs.items():
            self._headers.update({k.title(): v})

    def get(self, key):
        return self._headers.get(key)
