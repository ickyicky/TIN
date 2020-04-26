from server.parsers import HTTPParser
from server.handler import HTTPHandler
from server.worker import SocketListener

from router import router

import logging

logging.basicConfig(level=logging.DEBUG)

h = HTTPHandler(HTTPParser(), router=router)
server = SocketListener(h, address="0.0.0.0", port=12345)

server.serve()
