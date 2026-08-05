import sys
import httpx

# Since aiohttp_shim is only imported when aiohttp is present, get the real aiohttp module from sys.modules
real_aiohttp = sys.modules.get("aiohttp")

class ContentTypeError(Exception):
    pass

class ClientTimeout:
    def __init__(self, *args, **kwargs):
        pass

class TCPConnector:
    def __init__(self, *args, **kwargs):
        pass

class HttpxResponseWrapper:
    def __init__(self, response: httpx.Response):
        self._response = response

    @property
    def status(self):
        return self._response.status_code

    @property
    def ok(self):
        return self._response.is_success

    async def json(self):
        try:
            return self._response.json()
        except Exception as e:
            raise ContentTypeError(f"Failed to decode JSON: {e}")

    async def text(self):
        return self._response.text

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

class HttpxSessionWrapper:
    def __init__(self, async_client: httpx.AsyncClient):
        self._client = async_client

    @property
    def loop(self):
        import asyncio
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.get_event_loop()

    def post(self, url, **kwargs):
        return HttpxRequestCtxManager(self._client, "POST", url, **kwargs)

    def patch(self, url, **kwargs):
        return HttpxRequestCtxManager(self._client, "PATCH", url, **kwargs)

    def put(self, url, **kwargs):
        return HttpxRequestCtxManager(self._client, "PUT", url, **kwargs)

    def get(self, url, **kwargs):
        return HttpxRequestCtxManager(self._client, "GET", url, **kwargs)

    def delete(self, url, **kwargs):
        return HttpxRequestCtxManager(self._client, "DELETE", url, **kwargs)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

class HttpxRequestCtxManager:
    def __init__(self, client: httpx.AsyncClient, method: str, url: str, **kwargs):
        self._client = client
        self._method = method
        self._url = url
        # Remove any aiohttp-specific args
        if "timeout" in kwargs:
            kwargs.pop("timeout")
        self._kwargs = kwargs
        self._response = None

    async def __aenter__(self):
        resp = await self._client.request(self._method, self._url, **self._kwargs)
        self._response = HttpxResponseWrapper(resp)
        return self._response

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

class ClientSession:
    def __init__(self, *args, **kwargs):
        from shared_client.client import MDRClient
        self._mdr_client = MDRClient()
        self._wrapper = HttpxSessionWrapper(self._mdr_client.async_client)

    async def __aenter__(self):
        return self._wrapper

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._mdr_client.aclose()

def __getattr__(name):
    if real_aiohttp is None:
        raise AttributeError(f"module 'aiohttp' has no attribute '{name}' (and real aiohttp is not installed)")
    return getattr(real_aiohttp, name)
