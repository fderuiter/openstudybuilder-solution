import sys
from shared_client.client import MDRClient

# Since requests_shim is only imported when requests is present, get the real requests module from sys.modules
real_requests = sys.modules.get("requests")

_shared_client = None

def _get_client():
    global _shared_client
    if _shared_client is None:
        _shared_client = MDRClient()
    return _shared_client.client

def get(url, **kwargs):
    return _get_client().get(url, **kwargs)

def post(url, **kwargs):
    return _get_client().post(url, **kwargs)

def patch(url, **kwargs):
    return _get_client().patch(url, **kwargs)

def put(url, **kwargs):
    return _get_client().put(url, **kwargs)

def delete(url, **kwargs):
    return _get_client().delete(url, **kwargs)

def request(method, url, **kwargs):
    return _get_client().request(method, url, **kwargs)

def head(url, **kwargs):
    return _get_client().head(url, **kwargs)

def options(url, **kwargs):
    return _get_client().options(url, **kwargs)

class ApiShim:
    @staticmethod
    def request(method, url, **kwargs):
        return _get_client().request(method, url, **kwargs)
    @staticmethod
    def get(url, **kwargs):
        return _get_client().get(url, **kwargs)
    @staticmethod
    def post(url, **kwargs):
        return _get_client().post(url, **kwargs)
    @staticmethod
    def patch(url, **kwargs):
        return _get_client().patch(url, **kwargs)
    @staticmethod
    def put(url, **kwargs):
        return _get_client().put(url, **kwargs)
    @staticmethod
    def delete(url, **kwargs):
        return _get_client().delete(url, **kwargs)
    @staticmethod
    def head(url, **kwargs):
        return _get_client().head(url, **kwargs)
    @staticmethod
    def options(url, **kwargs):
        return _get_client().options(url, **kwargs)

api = ApiShim()

def __getattr__(name):
    if real_requests is None:
        raise AttributeError(f"module 'requests' has no attribute '{name}' (and real requests is not installed)")
    return getattr(real_requests, name)
