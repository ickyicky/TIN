class HTTPRequest:
    def __init__(self, headers, method, data=None):
        self.headers = headers
        self.method = method
        self.data = data
