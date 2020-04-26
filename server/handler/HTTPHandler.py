import logging
import enum
import traceback
from ..router import Router
from ..response import HTTPResponse, Statuses

log = logging.getLogger(__name__)


class HTTPHandler:
    def __init__(self, parser, router, middleware=[], packet_size=4096):
        """
        HTTP request handler. Handles new connection.
        """
        self.packet_size = packet_size
        self.parser = parser
        self.router = router
        self.middleware = middleware

    def parse_request(self, conn):
        """
        Parse request using self.parser and wait for full packet
        for beeing transfered (receive full data)
        """
        initial_data = conn.recv(self.packet_size)
        headers, method, data = self.parser(initial_data)

        while len(data) < int(headers.get("content-length", 0)):
            data += conn.recv(self.packet_size)

        return headers, method, data

    def return_(self, conn, response):
        """
        Produce response object.
        """
        conn.send(response.encode())

    def __call__(self, conn):
        """
        Make handler object calklable to handle request
        """
        try:
            headers, method, data = self.parse_request(conn)
        except Exception as e:
            log.warn("Request prasing error: {}", str(e))

        for middleware in self.middleware:
            status, error = middleware(headers, method, data)
            if error:
                self.return_(conn, status, error)

        try:
            method_func = self.router.route(method)
            response = method_func(data=data)
        except Router.MethodNotFound as e:
            status = Statuses.NOT_FOUND
            response = HTTPResponse(status)
            log.warn(str(e))
        except Router.MethodNotAllowed as e:
            status = Statuses.NOT_ALLOWED
            response = HTTPResponse(status)
            log.warn(str(e))
        except Exception as e:
            status = Statuses.SERVER_ERROR
            response = HTTPResponse(status, traceback.format_exc())
            log.exception(e)

        self.return_(conn, response)
