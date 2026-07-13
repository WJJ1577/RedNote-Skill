"""x-s-common header generation.

The x-s-common header contains platform metadata encoded as
a comma-separated key=value string. This is a critical part
of the request signing chain.

References:
  - RedCrack header/X_S_Common.py
"""


def generate_x_s_common(
    a1: str,
    web_session: str = "",
    timestamp: str = "",
) -> dict[str, str]:
    """Generate the x-s-common header value.

    Args:
        a1: The a1 cookie value (device fingerprint)
        web_session: The web_session cookie (login token, may be empty)
        timestamp: Millisecond timestamp string

    Returns:
        Dict with 'x-s-common' key containing the encoded header value
    """
    # Platform ID constants
    PLATFORM_ID = "1"  # Web platform
    BUILD = "1"        # Build version

    # Construct the x-s-common payload
    # Format: platform=1;;aid=xxx;;sm=...;;build=1;;ts=...
    parts = [
        f"platform={PLATFORM_ID}",
        "",
        f"aid={a1}",
        "",
        "",  # sm (session metadata)
        "",
        "",  # sv (sign version)
        "",
        f"build={BUILD}",
        "",
    ]

    if timestamp:
        parts.append(f"ts={timestamp}")
        parts.append("")

    raw = ";".join(parts)

    return {"x-s-common": raw}
