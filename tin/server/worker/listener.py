import socket
import logging
from _thread import start_new_thread

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
        self.socket = None

    def init_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log.debug("Socket initialized")

        self.socket.bind(self.addr)
        log.debug(f"Socket bound to addr: {self.addr}")

        if self.ssl_context:
            self.socket = self.ssl_context.wrap_socket(self.socket, server_side=True)
            log.debug(f"Socket ssl context set")

    def listen(self):
        """
        listens on given socket
        """
        self.socket.listen()

    def receive(self):
        """
        Procedure for receiving single request
        """
        self._receive(self.socket)

    def serve(self):
        """
        Seves threaded handlers for each connection
        """
        self.init_socket()
        self.listen()
        # TODO
        while True:
            self.receive()

        self.close()

    def _receive(self, socket):
        conn, addr = socket.accept()

        log.debug(f"Received connection from {addr}")
        start_new_thread(self.handler, (conn,))

    def close(self):
        self.socket.close()
