# tests/test_middleware.py
import pytest
import httpx
from rednote_core.client.middleware import RequestSigner


async def _apply_signer(signer: RequestSigner, request: httpx.Request) -> httpx.Request:
    """Apply signer via async auth flow and return the signed request."""
    async for signed in signer.async_auth_flow(request):
        return signed
    return request


class TestRequestSigner:
    @pytest.mark.asyncio
    async def test_injects_signature_headers(self):
        cookies = {
            "a1": "a" * 32,
            "web_session": "test_session",
            "webId": "b" * 32,
            "gid": "c" * 16,
            "websectiga": "d" * 32,
        }
        signer = RequestSigner(cookies)

        request = httpx.Request(
            method="GET",
            url="https://edith.xiaohongshu.com/api/sns/web/v1/test",
        )

        signed = await _apply_signer(signer, request)

        assert "x-s" in signed.headers
        assert "x-s-common" in signed.headers
        assert "x-t" in signed.headers
        assert "x-b3-traceid" in signed.headers
        assert "x-xray-traceid" in signed.headers

    @pytest.mark.asyncio
    async def test_preserves_existing_headers(self):
        cookies = {"a1": "a" * 32, "web_session": ""}
        signer = RequestSigner(cookies)

        request = httpx.Request(
            method="GET",
            url="https://edith.xiaohongshu.com/api/test",
            headers={"User-Agent": "TestAgent/1.0", "Content-Type": "application/json"},
        )

        signed = await _apply_signer(signer, request)

        assert signed.headers["User-Agent"] == "TestAgent/1.0"
        assert signed.headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_different_requests_different_signatures(self):
        cookies = {"a1": "a" * 32, "web_session": ""}
        signer = RequestSigner(cookies)

        r1 = httpx.Request("GET", "https://edith.xiaohongshu.com/api/a")
        r2 = httpx.Request("GET", "https://edith.xiaohongshu.com/api/b")

        s1 = await _apply_signer(signer, r1)
        s2 = await _apply_signer(signer, r2)

        assert s1.headers["x-s"] != s2.headers["x-s"]
