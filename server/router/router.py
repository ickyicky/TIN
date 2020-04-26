import logging
import re
from collections import namedtuple

log = logging.getLogger(__name__)


class Router:
    class MethodNotAllowed(Exception):
        """
        Raised when router doesnt have registered function
        for handling requested method on requested path.
        """

        pass

    class MethodNotFound(Exception):
        """
        Raised when requested path is not registered.
        """

        pass

    Endpoint = namedtuple("Endpoint", ("method", "path", "func"))
    Path = namedtuple("Path", ("method", "path_raw"))

    def __init__(self, endpoints=[]):
        """
        Initialization from  given endpoints. For information about enpoint
        data format check endpoint class or register function description.
        """
        self.endpoints = {}
        for endpoint in endpoints:
            self.register(endpoint)

    def _extract_data(self, endpoint):
        """
        This function validates path
        """
        method, path_raw, func = endpoint
        return method, path_raw, func

    def _extract_path(self, path_raw):
        """
        Extracts parameters from path and matches it to
        registered endpoint.
        """
        method, path_raw = path_raw
        params = {}

        try:
            path_raw, params = path_raw.split("?")

            params = params.split("&")
            params = dict(p.split("=") for p in params)
            log.debug("Params:", params)
        except Exception as e:
            log.debug("Parsing params failed due to error:", e)

        for path, methods in self.endpoints.items():
            if re.match(path, path_raw):
                log.debug(f"{path_raw} matches {path}")
                try:
                    func = methods[method]
                except KeyError:
                    raise self.MethodNotAllowed(path_raw)

                path_params = re.search(path, path_raw)
                if path_params:
                    params.update(path_params.groupdict())

                return func, params

        raise self.MethodNotFound(path_raw)

    def register(self, endpoint):
        """
        Registers given endpoint.
        Endpoint = (method, path, func)
        Path params should be soecified in patterns format.
        """
        method, path, func = self._extract_data(endpoint)

        if path not in self.endpoints:
            log.debug(f"registering new endpoint: {path}")
            self.endpoints[path] = {}

        if method in self.endpoints[path]:
            log.warn(f"overriding existing method {method} {path}")

        log.debug(f"registering method {method} {path}")
        self.endpoints[path][method] = func

    def route(self, path_raw):
        """
        Returns parametrizied function for given raw path
        """
        func, params = self._extract_path(path_raw)

        def parametrizied(*args, **kwargs):
            return func(*args, **params, **kwargs)

        return parametrizied
