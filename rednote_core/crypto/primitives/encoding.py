"""Encoding and byte-manipulation primitives."""

import base64


def base64_encode(data: bytes) -> str:
    """Encode bytes to Base64 string.

    Args:
        data: Raw bytes

    Returns:
        Base64-encoded string
    """
    return base64.b64encode(data).decode("ascii")


def base64_decode(s: str) -> bytes:
    """Decode Base64 string to bytes.

    Args:
        s: Base64-encoded string

    Returns:
        Decoded raw bytes
    """
    return base64.b64decode(s)


def hex_encode(data: bytes) -> str:
    """Encode bytes to hex string (lowercase, no prefix).

    Args:
        data: Raw bytes

    Returns:
        Hex string
    """
    return data.hex()


def hex_decode(s: str) -> bytes:
    """Decode hex string to bytes.

    Args:
        s: Hex string (with or without '0x' prefix)

    Returns:
        Decoded raw bytes
    """
    s = s.lower()
    if s.startswith("0x"):
        s = s[2:]
    return bytes.fromhex(s)


def int_to_bytes(n: int, length: int) -> bytes:
    """Convert integer to big-endian bytes of fixed length.

    Args:
        n: Integer value
        length: Number of output bytes

    Returns:
        Big-endian byte representation
    """
    return n.to_bytes(length, byteorder="big")


def bytes_to_int(data: bytes) -> int:
    """Convert big-endian bytes to integer.

    Args:
        data: Big-endian bytes

    Returns:
        Integer value
    """
    return int.from_bytes(data, byteorder="big")


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two byte sequences.

    Args:
        a: First byte sequence
        b: Second byte sequence (must be same length)

    Returns:
        XOR result

    Raises:
        ValueError: If inputs have different lengths
    """
    if len(a) != len(b):
        raise ValueError(
            f"Length mismatch: {len(a)} != {len(b)}"
        )
    return bytes(x ^ y for x, y in zip(a, b))
