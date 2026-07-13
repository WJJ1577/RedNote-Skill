"""x-rap-param header generation.

The x-rap-param header contains encrypted device fingerprint data
used for risk assessment. It uses AES-CBC encryption with a
derived key based on device attributes.

This is a critical anti-bot parameter. The full implementation
requires reverse-engineering the exact JSON structure and key
derivation from the Xiaohongshu web SDK.

For v1, we provide a minimal implementation that generates
the expected format. Full device fingerprinting can be
enhanced in later iterations.

References:
  - RedCrack header/X_Rap_Param.py
"""

import json
import uuid
import time
from rednote_core.crypto.primitives.symmetric import aes_cbc_encrypt
from rednote_core.crypto.primitives.hash import md5
from rednote_core.crypto.primitives.encoding import base64_encode


def generate_x_rap_param() -> dict[str, str]:
    """Generate the x-rap-param header with device fingerprint.

    Returns:
        Dict with 'x-rap-param' key containing encrypted device info
    """
    device_id = str(uuid.uuid4()).replace("-", "")[:16]
    timestamp_ms = str(int(time.time() * 1000))

    device_info = {
        "deviceId": device_id,
        "platform": "web",
        "timestamp": timestamp_ms,
        "version": "1.0.0",
    }

    # Encrypt with derived key
    key = md5(device_id.encode())  # 16 bytes for AES-128
    iv = md5(timestamp_ms.encode())  # 16 bytes IV

    plaintext = json.dumps(device_info, separators=(",", ":")).encode()
    ciphertext = aes_cbc_encrypt(key, iv, plaintext)
    encoded = base64_encode(ciphertext)

    return {"x-rap-param": encoded}
