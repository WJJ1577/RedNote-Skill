"""a1 and webId cookie generation.

References:
  - RedCrack cookie/a1_and_webId.py
"""

import uuid
import random
import time
from rednote_core.crypto.primitives.hash import md5


def generate_a1() -> str:
    """Generate the a1 device identifier cookie.

    Format: hex string derived from random UUID + timestamp.

    Returns:
        32-character hex a1 value
    """
    raw = f"{uuid.uuid4().hex}{time.time()}{random.random()}"
    return md5(raw.encode()).hex()


def generate_web_id() -> str:
    """Generate the webId session identifier cookie.

    Format: 32-character hex string (UUID4 without dashes).

    Returns:
        32-character hex webId value
    """
    return uuid.uuid4().hex
