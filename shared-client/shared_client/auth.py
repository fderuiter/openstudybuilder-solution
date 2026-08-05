import os
import time
import logging
import httpx
import httpx_auth

logger = logging.getLogger("shared_client.auth")

class LazyOAuth2ClientCredentials(httpx.Auth):
    def __init__(self, token_endpoint, client_id, client_secret, scope):
        self.token_endpoint = token_endpoint
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.access_token = None
        self.expires_at = 0

    def _is_token_expired(self):
        if not self.access_token:
            return True
        # Refresh if less than 60 seconds left before expiration
        return time.time() + 60 > self.expires_at

    def _refresh_token(self):
        logger.info("Refreshing OAuth2 client credentials token passively...")
        try:
            response = httpx.post(
                self.token_endpoint,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials",
                    "scope": self.scope,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            payload = response.json()
            self.access_token = payload["access_token"]
            expires_in = payload.get("expires_in", 3600)
            self.expires_at = time.time() + expires_in
            logger.info("Successfully refreshed OAuth2 token.")
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            raise

    async def _arefresh_token(self):
        logger.info("Refreshing OAuth2 client credentials token passively (async)...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_endpoint,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "grant_type": "client_credentials",
                        "scope": self.scope,
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                payload = response.json()
                self.access_token = payload["access_token"]
                expires_in = payload.get("expires_in", 3600)
                self.expires_at = time.time() + expires_in
                logger.info("Successfully refreshed OAuth2 token (async).")
        except Exception as e:
            logger.error(f"Failed to refresh token (async): {e}")
            raise

    def sync_auth_flow(self, request):
        if self._is_token_expired():
            self._refresh_token()
        if self.access_token:
            request.headers["Authorization"] = f"Bearer {self.access_token}"
        yield request

    async def async_auth_flow(self, request):
        if self._is_token_expired():
            await self._arefresh_token()
        if self.access_token:
            request.headers["Authorization"] = f"Bearer {self.access_token}"
        yield request


def get_auth_handler(
    client_id: str = None,
    client_secret: str = None,
    token_endpoint: str = None,
    auth_endpoint: str = None,
    scope: str = None,
    api_token: str = None
):
    """
    Returns an appropriate httpx.Auth instance or None based on inputs or environment.
    """
    # Load from environment if not specified
    client_id = client_id or os.environ.get("CLIENT_ID", "")
    client_secret = client_secret or os.environ.get("CLIENT_SECRET", "")
    token_endpoint = token_endpoint or os.environ.get("TOKEN_ENDPOINT", "")
    auth_endpoint = auth_endpoint or os.environ.get("AUTH_ENDPOINT", "")
    scope = scope or os.environ.get("SCOPE", "")
    api_token = api_token or os.environ.get("STUDYBUILDER_API_TOKEN", "")

    if api_token:
        logger.info("Using static STUDYBUILDER_API_TOKEN")
        class StaticTokenAuth(httpx.Auth):
            def __init__(self, token):
                self.token = token
            def sync_auth_flow(self, request):
                request.headers["Authorization"] = f"Bearer {self.token}"
                yield request
            async def async_auth_flow(self, request):
                request.headers["Authorization"] = f"Bearer {self.token}"
                yield request
        return StaticTokenAuth(api_token)

    elif client_id:
        if client_secret:
            logger.info("Using LazyOAuth2ClientCredentials")
            return LazyOAuth2ClientCredentials(
                token_endpoint=token_endpoint,
                client_id=client_id,
                client_secret=client_secret,
                scope=scope
            )
        else:
            logger.info("Using interactive OAuth2AuthorizationCodePKCE")
            return httpx_auth.OAuth2AuthorizationCodePKCE(
                authorization_url=auth_endpoint,
                token_url=token_endpoint,
                client_id=client_id,
                scope=scope,
            )
    else:
        logger.info("No authentication config found")
        return None
