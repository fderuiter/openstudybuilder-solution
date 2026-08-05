import sys
import httpx
from . import requests_shim
from . import aiohttp_shim

sys.modules["requests"] = requests_shim
sys.modules["aiohttp"] = aiohttp_shim

# Monkeypatch httpx.Response to behave more like requests.Response for backward compatibility
if not hasattr(httpx.Response, "ok"):
    @property
    def httpx_ok(self):
        return self.is_success
    httpx.Response.ok = httpx_ok

if not hasattr(httpx.Response, "reason"):
    @property
    def httpx_reason(self):
        return self.reason_phrase
    httpx.Response.reason = httpx_reason
