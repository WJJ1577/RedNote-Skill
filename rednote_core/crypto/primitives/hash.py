"""Hash function primitives."""

import hashlib
import hmac as hmac_module


def md5(data: bytes) -> bytes:
    """Compute MD5 hash of data.

    Args:
        data: Input data

    Returns:
        16-byte MD5 digest
    """
    return hashlib.md5(data).digest()


def sha256(data: bytes) -> bytes:
    """Compute SHA-256 hash of data.

    Args:
        data: Input data

    Returns:
        32-byte SHA-256 digest
    """
    return hashlib.sha256(data).digest()


def hmac_sha256(key: bytes, data: bytes) -> bytes:
    """Compute HMAC-SHA256 of data with given key.

    Args:
        key: HMAC secret key
        data: Data to authenticate

    Returns:
        32-byte HMAC digest
    """
    return hmac_module.new(key, data, hashlib.sha256).digest()
