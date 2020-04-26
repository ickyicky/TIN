import logging

log = logging.getLogger(__name__)


class HTTPParser:
    def __init__(self):
        pass

    def __call__(self, data):
        """
        Callable method for parsing request
        TODO HTTPRequest class
        """
        headers_data, request_data = data.split(b"\r\n\r\n")
        headers_data = headers_data.split(b"\r\n")

        method, path, protocol = headers_data[0].decode().split(" ")

        headers = {"protocol": protocol}

        for line in headers_data[1:]:
            k, v = line.decode().lower().split(": ")
            headers[k] = v

        log.debug("headers:", str(headers))
        log.debug("method:", str(method))
        log.debug("path:", str(path))
        log.debug("request_data", str(request_data))

        return headers, (method, path), request_data
