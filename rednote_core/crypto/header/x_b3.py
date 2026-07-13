"""x-b3-traceid header generation.

Format: 32 hex characters (16 random bytes).

References:
  - RedCrack header/X_B3.py
"""

import uuid


def generate_x_b3_traceid() -> str:
    """Generate x-b3-traceid header value.

    Returns:
        32-character hex trace ID
    """
    return uuid.uuid4().hex
