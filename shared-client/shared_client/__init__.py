import sys
import httpx

# Try importing the real modules first
try:
    import requests as real_requests
    _has_requests = True
except ModuleNotFoundError:
    real_requests = None
    _has_requests = False

try:
    import aiohttp as real_aiohttp
    _has_aiohttp = True
except ModuleNotFoundError:
    real_aiohttp = None
    _has_aiohttp = False

# Import and install shims conditionally
if _has_requests:
    from . import requests_shim
    sys.modules["requests"] = requests_shim

if _has_aiohttp:
    from . import aiohttp_shim
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
