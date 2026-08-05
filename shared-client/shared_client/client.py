import os
import ssl
import sys
import logging
import httpx
from .auth import get_auth_handler

logger = logging.getLogger("shared_client.client")

class MDRClient:
    def __init__(self, api_base_url: str = None, timeout: float = 60.0):
        self.api_base_url = api_base_url or os.environ.get("API_BASE_URL", "")
            
        # Get CA bundle if present
        ca_bundle = os.environ.get("REQUESTS_CA_BUNDLE", "")
        if ca_bundle:
            context = ssl.create_default_context(cafile=ca_bundle)
        else:
            context = None

        self.auth = get_auth_handler()
        
        # Instantiate sync httpx Client
        self.client = httpx.Client(
            base_url=self.api_base_url or None,
            auth=self.auth,
            verify=context,
            timeout=timeout
        )
        self.client.headers.update({"Accept": "application/json", "User-Agent": "test"})
        
        # Instantiate async httpx Client
        self.async_client = httpx.AsyncClient(
            base_url=self.api_base_url or None,
            auth=self.auth,
            verify=context,
            timeout=timeout
        )
        self.async_client.headers.update({"Accept": "application/json", "User-Agent": "test"})

    def verify_connection(self, headers: dict = None):
        if not self.api_base_url:
            logger.critical("API_BASE_URL is not set.")
            sys.exit(1)
        try:
            # Both utilities use this unified routine
            response = self.client.get("openapi.json", headers=headers)
            response.raise_for_status()
            logger.info(f"Connected to api at {self.api_base_url} successfully via shared client.")
        except Exception as e:
            logger.critical(
                f"Failed to connect to backend, is it running?\nError was:\n{e}"
            )
            sys.exit(1)

    def close(self):
        self.client.close()

    async def aclose(self):
        await self.async_client.aclose()
