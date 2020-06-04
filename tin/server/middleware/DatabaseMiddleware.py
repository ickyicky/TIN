import logging

log = logging.getLogger(__name__)


class DatabaseMiddleware:
    def __init__(self, dbssn_factory):
        self.dbssn_factory = dbssn_factory

    def process_request(self, request):
        request.dbssn = self.dbssn_factory()

    def process_response(self, response, request):
        try:
            request.dbssn.close()
        except AttributeError:
            pass
