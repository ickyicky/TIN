import logging
from .domain import PathLock
from .server.response import Statuses
from .server.handler.HTTPExceptions import HTTPException


class ResourceGuardian:
    """
    Class, that makes guarding concurrency actions on resources
    fairly easy. It sotres information about locked paths in db.
    """

    SAFE_OPERATIONS = (PathLock.Method.read.value, PathLock.Method.read.value)

    def __init__(self, request):
        self.path = None
        self.request = request
        self.current_locks = []
        self.operation = None
        self.lock = None

    def prepare(self, path, operation):
        self.path = path
        self.operation = operation

    def fetch_current_locks(self):
        self.current_locks = self.request.dbssn.query(PathLock).all()

    def interferes(self, lock):
        if self.path.startswith(lock.path) or lock.path.startswith(self.path):
            operations = (self.operation.value, lock.operation)
            if operations not in self.SAFE_OPERATIONS:
                return True

    def perform_lock(self):
        self.fetch_current_locks()
        for lock in self.current_locks:
            if self.interferes(lock):
                raise HTTPException(status=Statuses.LOCKED, message="Resource locked")

        lock = PathLock(path=self.path, method=self.operation.value)
        self.request.dbssn.add(lock)
        self.request.dbssn.commit()
        self.lock = lock

    def release(self):
        self.request.dbssn.delete(self.lock)
        self.request.dbssn.commit()


class ResourceGuardianMidddleware:
    def __init__(self):
        pass

    def process_request(self, request):
        request.resource_guardian = ResourceGuardian(request)

    def process_response(self, response, request):
        if request.resource_guardian.lock is not None:
            request.resource_guardian.release()


class lock_path:
    Method = PathLock.Method

    def __init__(self, path_arg, operation):
        self.path_arg = path_arg
        self.operation = operation

    def __call__(self, func):
        def wrapper(*args, request, **kwargs):
            request.resource_guardian.prepare(
                kwargs.get(self.path_arg, ""), self.operation
            )
            request.resource_guardian.perform_lock()
            return func(*args, request=request, **kwargs)

        return wrapper
