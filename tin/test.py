from server.parsers import HTTPParser
from server.handler import HTTPHandler
from server.worker import SocketListener
from server.router import Router
from server.response import Statuses, HTTPResponse


def hello(query, data=None):
    return HTTPResponse(Statuses.OK, query)


r = Router([("POST", "/hello", hello)])
h = HTTPHandler(HTTPParser(), router=r)
s = SocketListener(h, port=8080)

s.serve()
