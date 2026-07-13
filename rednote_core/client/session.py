"""XHSClient — the main HTTP client for Xiaohongshu API.

Wraps httpx.AsyncClient with automatic:
  - Cookie injection
  - Request signing (6 security headers)
  - Retry on 429/461
  - Proxy support
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

from rednote_core.client.middleware import RequestSigner, RetryMiddleware
from rednote_core.client.exceptions import AuthError

logger = logging.getLogger(__name__)

# Base URLs
EDITH_BASE = "https://edith.xiaohongshu.com"
API_BASE = "https://www.xiaohongshu.com"

DEFAULT_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


class XHSClient:
    """Async HTTP client for Xiaohongshu API.

    Usage:
        client = XHSClient(proxy="http://127.0.0.1:7890", cookies={...})
        resp = await client.get("/api/sns/web/v1/user/me")
    """

    def __init__(
        self,
        proxy: str,
        cookies: dict[str, str],
        *,
        timeout: float = 30.0,
        retry_interval: float = 5.0,
        request_interval: float = 2.0,
        user_agent: str = DEFAULT_UA,
    ):
        self._cookies = dict(cookies)
        self._proxy = proxy
        self._request_interval = request_interval

        # Build auth handler
        self._signer = RequestSigner(self._cookies)

        # Build retry handler
        self._retry = RetryMiddleware(
            max_retries=3,
            base_delay=retry_interval,
            on_461=self._on_461,
        )

        # Build httpx client
        self._client = httpx.AsyncClient(
            auth=self._signer,
            proxy=proxy,
            timeout=httpx.Timeout(timeout),
            headers={
                "User-Agent": user_agent,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Origin": "https://www.xiaohongshu.com",
                "Referer": "https://www.xiaohongshu.com/",
            },
            follow_redirects=True,
            http2=True,
        )

    @property
    def cookies(self) -> dict[str, str]:
        """Current cookies (read-only view)."""
        return dict(self._cookies)

    def update_cookies(self, new_cookies: dict[str, str]) -> None:
        """Merge new cookies into the current set.

        Args:
            new_cookies: Dict of cookie name -> value to add/update
        """
        self._cookies.update(new_cookies)

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
        data: Optional[dict] = None,
        headers: Optional[dict] = None,
        **kwargs,
    ) -> httpx.Response:
        """Make an HTTP request with full middleware chain.

        Args:
            method: HTTP method
            url: Full URL or path (paths are resolved against API_BASE)
            params: Query parameters
            json_data: JSON body (Content-Type: application/json)
            data: Form-encoded body
            headers: Additional headers

        Returns:
            httpx.Response object
        """
        import asyncio

        # Resolve relative URLs
        if not url.startswith("http"):
            if "/api/sns/web/v2/login" in url:
                base = EDITH_BASE
            else:
                base = API_BASE
            url = f"{base}{url}" if url.startswith("/") else f"{base}/{url}"

        # Inject cookies
        cookie_header = "; ".join(
            f"{k}={v}" for k, v in self._cookies.items() if v
        )
        merged_headers = {"Cookie": cookie_header}
        if headers:
            merged_headers.update(headers)

        # Rate limiting between requests
        await asyncio.sleep(self._request_interval)

        # Build and send
        request = self._client.build_request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            data=data,
            headers=merged_headers,
            **kwargs,
        )

        # Run through retry middleware
        async def next_handler(req: httpx.Request) -> httpx.Response:
            return await self._client.send(req)

        return await self._retry(request, next_handler)

    async def get(
        self, url: str, *, params: Optional[dict] = None, **kwargs
    ) -> httpx.Response:
        """Convenience GET request."""
        return await self.request("GET", url, params=params, **kwargs)

    async def post(
        self,
        url: str,
        *,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
        data: Optional[dict] = None,
        **kwargs,
    ) -> httpx.Response:
        """Convenience POST request."""
        return await self.request(
            "POST", url, params=params, json_data=json_data, data=data, **kwargs
        )

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    def _on_461(self) -> None:
        """Called when a 461 security challenge is hit."""
        logger.warning("461 received — crypto params may need refresh")
