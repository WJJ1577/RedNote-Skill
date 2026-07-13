"""websectiga cookie generation.

The websectiga cookie is a security token that involves
an MD5 hash of identifiers plus some random components.

References:
  - RedCrack cookie/websectiga.py
"""

import uuid
import time
import random
from rednote_core.crypto.primitives.hash import md5


def generate_websectiga() -> str:
    """Generate the websectiga security token cookie.

    Returns:
        websectiga hex string
    """
    raw = (
        f"{uuid.uuid4().hex}"
        f"{int(time.time() * 1000)}"
        f"{random.randint(0, 99999999)}"
    )
    return md5(raw.encode()).hex()
