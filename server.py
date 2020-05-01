from server.parsers import HTTPParser
from server.handler import HTTPHandler
from server.worker import SocketListener
from router import router
import logging
import ssl
import argparse

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
    logging.basicConfig(level=logging.DEBUG)

    h = HTTPHandler(HTTPParser(), router=router)
    server = SocketListener(h, address="0.0.0.0", port=12345, ssl_context=context)

    server.serve()
