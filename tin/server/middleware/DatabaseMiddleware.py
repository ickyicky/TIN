class DatabaseMiddleware:
    def __init__(self, dbssn_factory):
        self.dbssn_factory = dbssn_factory

    def process_request(self, request):
        request.dbssn = self.dbssn_factory()

    def process_response(self, request, response):
        pass
