from server.parsers import HTTPParser
from server.handler import HTTPHandler
from server.worker import SocketListener
from server.middleware.AuthGuardian import AuthGuardian
from router import router
import logging
import ssl
import argparse

LOG_FORMAT = "%(asctime)s.%(msecs)03d %(process)s.%(thread)s %(levelname)7s: %(name)s %(message)s"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--ssl", help="SSL", action="store_true")
    args = parser.parse_args()

    if args.ssl:
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

        server_cert = "certificate.crt"
        server_key = "privateKey.key"

        context.load_cert_chain(certfile=server_cert, keyfile=server_key)
    else:
        context = None
    logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG)

    class auth:
        def __init__(self):
            pass

        def authorize(self, token):
            if token and token == "ASD123":
                return True

    auth_module = auth()

    h = HTTPHandler(HTTPParser(), router=router, middleware=[AuthGuardian(auth_module)])
    server = SocketListener(h, address="0.0.0.0", port=12345, ssl_context=context)

    server.serve()
