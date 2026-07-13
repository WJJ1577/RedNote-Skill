"""HTTP middleware for automatic request signing and retry logic."""

from __future__ import annotations

import time
import logging
from typing import Optional

import httpx

from rednote_core.crypto import sign_request
from rednote_core.client.exceptions import (
    CryptoError,
    AuthError,
    RateLimitError,
    SecurityChallenge,
)

logger = logging.getLogger(__name__)


class RequestSigner:
    """httpx auth handler that injects Xiaohongshu security headers.

    This is the core middleware — every request passes through it
    to have x-s, x-s-common, x-t, x-b3-traceid, x-xray-traceid,
    and x-rap-param injected automatically.
    """

    def __init__(self, cookies: dict[str, str]):
        self._cookies = cookies

    async def async_auth_flow(
        self, request: httpx.Request
    ) -> httpx.Request:
        """Inject signature headers into the request."""
        try:
            # Build body string for signing
            body = None
            if request.content:
                body = request.content.decode("utf-8", errors="replace")

            # Generate all 6 signature headers
            extra_headers = sign_request(
                method=request.method,
                url=str(request.url),
                data=body,
                cookies=self._cookies,
                headers=dict(request.headers),
            )

            # Merge into request
            for key, value in extra_headers.items():
                request.headers[key] = value

        except Exception as e:
            raise CryptoError(f"Failed to sign request: {e}") from e

        yield request  # httpx auth flow protocol


class RetryMiddleware:
    """httpx transport wrapper that handles 429 and 461 responses."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 5.0,
        on_461=None,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.on_461 = on_461  # Callback to refresh crypto params

    async def __call__(
        self,
        request: httpx.Request,
        next_handler,
    ) -> httpx.Response:
        for attempt in range(self.max_retries + 1):
            response = await next_handler(request)

            if response.status_code == 200:
                return response

            if response.status_code == 461:
                if self.on_461 and attempt == 0:
                    logger.warning("461 security challenge, refreshing...")
                    self.on_461()
                    continue
                raise SecurityChallenge(
                    f"Security challenge on {request.url}"
                )

            if response.status_code == 429:
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt)
                    logger.warning(
                        f"Rate limited, waiting {delay:.0f}s (attempt {attempt + 1})"
                    )
                    time.sleep(delay)
                    continue
                raise RateLimitError(
                    f"Rate limited after {self.max_retries} retries"
                )

            if response.status_code in (401, 403):
                raise AuthError(
                    f"Auth failed ({response.status_code}) — re-run `rednote login`"
                )

            # Other errors — return as-is
            return response

        raise RateLimitError("Max retries exceeded")
