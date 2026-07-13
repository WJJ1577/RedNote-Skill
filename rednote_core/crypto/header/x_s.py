"""x-s request signature header generation.

x-s is the primary request signature. It's computed as:
  HMAC-SHA256(custom_encoded(path+params+body), key=derived_from_x_s_common)

References:
  - RedCrack header/X_S.py
"""

from __future__ import annotations

from rednote_core.crypto.primitives.hash import md5, hmac_sha256
from rednote_core.crypto.primitives.encoding import base64_encode


def generate_x_s(
    url: str,
    data: str | None,
    x_s_common: str,
    x_t: str,
    a1: str,
) -> str:
    """Generate the x-s signature header value.

    Args:
        url: Request URL path (e.g., /api/sns/web/v1/search/notes)
        data: Request body string (for POST), or None
        x_s_common: Value of x-s-common header
        x_t: Millisecond timestamp string
        a1: a1 cookie value

    Returns:
        x-s signature hex string
    """
    # Build the signing payload
    payload = url
    if data:
        payload += data

    # Create signing key from a1 + x_t
    key_material = f"{a1}{x_t}"
    sign_key = md5(key_material.encode())

    # Sign with HMAC-SHA256
    signature = hmac_sha256(sign_key, payload.encode())

    # Return as base64
    return base64_encode(signature)
