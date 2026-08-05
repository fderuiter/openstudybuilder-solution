import sys
import httpx
from shared_client.client import MDRClient

# Safely import the real requests module to delegate attributes
shim = sys.modules.pop("requests", None)
try:
    import requests as real_requests
except ModuleNotFoundError:
    real_requests = None
finally:
    if shim is not None:
        sys.modules["requests"] = shim

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

class ApiShim:
    @staticmethod
    def request(method, url, **kwargs):
        return _get_client().request(method, url, **kwargs)

api = ApiShim()

def __getattr__(name):
    if real_requests is None:
        raise AttributeError(f"module 'requests' has no attribute '{name}' (and real requests is not installed)")
    return getattr(real_requests, name)
