import logging
import socket
import enum
import traceback
from ..router import Router
from ..response import HTTPResponse, Statuses
from ..request import HTTPRequest
from ..headers import HTTPHeaders
from .HTTPExceptions import HTTPException

log = logging.getLogger(__name__)


class ClosedConnection(Exception):
    pass


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
        log.warn(initial_data)

        if not initial_data:
            raise ClosedConnection()

        headers, method, data = self.parser(initial_data)

        while len(data) < int(headers.get("Content-Length", 0)):
            data += conn.recv(self.packet_size)

        return headers, method, data

    def return_(self, conn, response):
        """
        Produce response object.
        """
        conn.send(response.encode())

    def receive(self, conn):
        """
        Function for receiving request
        """
        try:
            headers, method, data = self.parse_request(conn)
        except (ClosedConnection, socket.timeout):
            raise ClosedConnection()
        except Exception as e:
            log.warn(f"Request prasing error: {repr(e)}")
            raise HTTPException(status=Statuses.BAD_REQUEST, message="Invalid request")

        headers = HTTPHeaders(headers)

        return HTTPRequest(headers=headers, method=method, data=data)

    def handle_request(self, request):
        """
        Produces response for request
        """
        try:
            method_func = self.router.route(request.method)
            response = method_func(request=request)
        except Router.MethodNotFound as e:
            status = Statuses.NOT_FOUND
            response = HTTPResponse(status)
            log.warn(str(e))
        except Router.MethodNotAllowed as e:
            status = Statuses.NOT_ALLOWED
            response = HTTPResponse(status)
            log.warn(str(e))

        return response

    def process_request(self, request):
        """
        Process request by all middleware
        """
        for middleware in self.middleware:
            middleware.process_request(request)

    def process_response(self, response, request):
        """
        Process response by all middleware.
        I want to reverse the order so it kind of
        encapsulates request and allow for session
        closeing.
        """
        for middleware in self.middleware[::-1]:
            middleware.process_response(response, request)

    def __call__(self, conn):
        """
        Make handler object callable to handle request
        """

        close_connection = False

        while not close_connection:
            try:
                request = None
                try:
                    request = self.receive(conn)
                    self.process_request(request)
                    response = self.handle_request(request)
                except HTTPException as e:
                    log.warn(f"{e.status} {e.message}")
                    request = request or HTTPRequest({}, None)
                    response = HTTPResponse(e.status, e.message)
                except ClosedConnection:
                    close_connection = True
                    break

                self.process_response(response, request)
            except Exception as e:
                status = Statuses.SERVER_ERROR
                response = HTTPResponse(status, traceback.format_exc())
                log.exception(e)

            close_connection = response.close_connection()
            log.info(
                f"{response.status} {len(response.data) if response.data else 0} {response.headers._headers}"
            )
            self.return_(conn, response)
            if not close_connection:
                conn.settimeout(response.timeout())

        conn.close()
