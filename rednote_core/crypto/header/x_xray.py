"""x-xray-traceid header generation.

Format: hex timestamp + random hex, used for distributed tracing.

References:
  - RedCrack header/X_Xray.py
"""

import uuid
import time


def generate_x_xray_traceid() -> str:
    """Generate x-xray-traceid header value.

    Returns:
        Hex trace ID string (timestamp + random)
    """
    ts_hex = hex(int(time.time()))[2:]  # Strip '0x'
    rand_hex = uuid.uuid4().hex[:8]
    return f"{ts_hex}{rand_hex}"
