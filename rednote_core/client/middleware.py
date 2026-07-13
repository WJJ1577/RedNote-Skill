"""HTTP middleware for automatic request signing and retry logic."""

from __future__ import annotations

import time
import logging
import typing
from typing import Optional

import httpx

from rednote_core.crypto import sign_request
from rednote_core.crypto.fingerprint import update_fingerprint
from rednote_core.client.exceptions import (
    CryptoError,
    AuthError,
    RateLimitError,
    SecurityChallenge,
)

logger = logging.getLogger(__name__)


class RequestSigner(httpx.Auth):
    """httpx Auth handler that injects Xiaohongshu security headers.

    This is the core middleware — every request passes through it
    to have x-s, x-s-common, x-t, x-b3-traceid, x-xray-traceid,
    and x-rap-param injected automatically.

    Subclasses httpx.Auth so httpx accepts it as a valid auth argument.

    IMPORTANT: mirrors RedCrack XHS_Session.__request_encrypt which
    updates loadts cookie AND fingerprint before EVERY request.
    """

    def __init__(self, cookies: dict[str, str], fp: dict | None = None):
        self._cookies = cookies
        self._fp = fp

    def auth_flow(
        self, request: httpx.Request
    ) -> typing.Generator[httpx.Request, httpx.Response, None]:
        """Inject signature headers into the request."""
        import time as _time

        try:
            # Per RedCrack __request_encrypt: update loadts BEFORE every request
            loadts = str(int(_time.time() * 1000))
            self._cookies["loadts"] = loadts

            # Update fingerprint (mirrors RedCrack update_fingerprint)
            if self._fp:
                update_fingerprint(self._fp, self._cookies, str(request.url))

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
                fp=self._fp,
            )

            # Merge into request
            for key, value in extra_headers.items():
                request.headers[key] = value

            # Remove httpx auto-added headers that trigger CDN WAF
            # These browser-fingerprint headers cause Akamai/TencentEdgeOne to
            # reject requests that don't have a full browser cookie set.
            # curl (which works) doesn't send these headers.
            # NOTE: keep 'host' — HTTP/1.1 requires it
            for hdr in (
                "accept-encoding",
                "connection",
                "sec-ch-ua",
                "sec-ch-ua-mobile",
                "sec-ch-ua-platform",
                "sec-fetch-dest",
                "sec-fetch-mode",
                "sec-fetch-site",
                "priority",
            ):
                request.headers.pop(hdr, None)

        except Exception as e:
            raise CryptoError(f"Failed to sign request: {e}") from e

        yield request


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
            try:
                response = await next_handler(request)
            except httpx.TransportError as e:
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt)
                    logger.warning(
                        f"Transport error: {e} — retrying in {delay:.0f}s "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(delay)
                    continue
                raise

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
