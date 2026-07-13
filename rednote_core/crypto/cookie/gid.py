"""gid cookie generation.

References:
  - RedCrack cookie/gid_webprofile_data.py
"""

import uuid
import time
import random
from rednote_core.crypto.primitives.hash import md5


def generate_gid() -> str:
    """Generate the gid global identifier cookie.

    Format: short hex hash.

    Returns:
        Hex gid value
    """
    raw = f"{uuid.uuid4().hex}{time.time()}{random.random()}"
    return md5(raw.encode()).hex()[:16]
