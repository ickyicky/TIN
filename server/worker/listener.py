import socket
import logging

log = logging.getLogger(__name__)


class SocketListener:
    """
    Simple HTTP/HTTPS SocketListener

    Requires parser, for parsing header and content_lenght from
    initial data (first received packet).
    """

    def __init__(self, handler, address="127.0.0.1", port=443, ssl_context=None):
        self.addr = (address, port)
        self.handler = handler
        self.ssl_context = ssl_context

        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        log.debug("Socket initialized")

        self.socket.bind(self.addr)
        log.debug(f"Socket bound to addr: {self.addr}")

    def listen(self):
        """
        listens on given socket
        """
        self.socket.listen()

    def receive(self):
        """
        Procedure for receiving single request
        """
        if self.ssl_context:
            with self.ssl_context.wrap_socket(self.socket, server_side=True) as socket:
                self._receive(socket)
        else:
            self._receive(self.socket)

    def serve(self):
        """
        Seves threaded handlers for each connection
        """
        self.listen()
        # TODO
        while True:
            self.receive()

    def _receive(self, socket):
        conn, addr = socket.accept()

        with conn:
            log.debug(f"Received connection from {addr}")
            self.handler(conn)

    def close(self):
        self.socket.close()
