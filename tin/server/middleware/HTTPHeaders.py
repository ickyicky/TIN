class HTTPHeaders:
    def __init__(self, cdtime=60, keep_alive=True):
        self.cdtime = cdtime
        self.keep_alive = keep_alive

    def process_request(self, request):
        pass

    def process_response(self, response, request=None):
        if self.keep_alive:
            response.headers.update({"Connection": "keep-alive"})
            response.headers.update({"Keep-Alive": f"timeout={self.cdtime}, max=1000"})
        else:
            response.headers.update({"Connection": "close"})

        if response.data:
            response.headers.update({"Content-Length": len(response.data)})
        else:
            response.headers.update({"Content-Length": 0})

        if "Content-Type" not in response.headers and response.data:
            response.headers.update({"Content-Type": "application/octet-stream"})

