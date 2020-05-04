import logging

log = logging.getLogger(__name__)


class HTTPParser:
    def __init__(self):
        pass

    def __call__(self, data):
        """
        Callable method for parsing request
        """
        headers_data, request_data = data.split(b"\r\n\r\n")
        headers_data = headers_data.split(b"\r\n")

        method, path, protocol = headers_data[0].decode().split(" ")

        headers = {"protocol": protocol}

        for line in headers_data[1:]:
            k, v = line.decode().split(": ")
            headers[k] = v

        log.debug(f"headers: {str(headers)}")
        log.debug(f"method: {str(method)}")
        log.debug(f"path: {str(path)}")
        log.debug(f"request_data head: {str(request_data)[:20]}")

        return headers, (method, path), request_data
