class HTTPException(Exception):
    def __init__(self, status, message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status = status
        self.message = message
