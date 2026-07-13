"""RedNote crypto module — cookie generation and request signing."""

from __future__ import annotations

import time
from urllib.parse import urlparse

from rednote_core.crypto.cookie.a1_webid import generate_a1, generate_web_id
from rednote_core.crypto.cookie.gid import generate_gid
from rednote_core.crypto.cookie.websectiga import generate_websectiga
from rednote_core.crypto.header.x_b3 import generate_x_b3_traceid
from rednote_core.crypto.header.x_xray import generate_x_xray_traceid
from rednote_core.crypto.header.x_s_common import generate_x_s_common
from rednote_core.crypto.header.x_s import generate_x_s
from rednote_core.crypto.header.x_rap_param import generate_x_rap_param


def generate_cookies() -> dict[str, str]:
    """Generate all locally-computable cookies.

    Returns a dict of cookie name -> value for:
      a1, webId, gid, websectiga

    web_session and sec_poison_id come from login / server
    and are NOT generated here.
    """
    return {
        "a1": generate_a1(),
        "webId": generate_web_id(),
        "gid": generate_gid(),
        "websectiga": generate_websectiga(),
    }


def sign_request(
    method: str,
    url: str,
    data: str | None,
    cookies: dict[str, str],
    headers: dict[str, str],
) -> dict[str, str]:
    """Sign an API request by generating all required security headers.

    Args:
        method: HTTP method (GET, POST, etc.)
        url: Full request URL
        data: Request body (for POST), or None
        cookies: Current cookie jar (dict of name -> value)
        headers: Current request headers

    Returns:
        Dict of header name -> value to add to the request
    """
    a1 = cookies.get("a1", "")
    web_session = cookies.get("web_session", "")
    timestamp = str(int(time.time() * 1000))

    # Generate x-s-common
    x_s_common_result = generate_x_s_common(a1, web_session, timestamp)
    x_s_common = x_s_common_result["x-s-common"]

    # Extract path + query
    parsed = urlparse(url)
    path_and_query = parsed.path
    if parsed.query:
        path_and_query += "?" + parsed.query

    # Generate x-s signature
    x_s = generate_x_s(path_and_query, data, x_s_common, timestamp, a1)

    # Generate x-rap-param
    rap = generate_x_rap_param()

    result = {
        "x-s": x_s,
        "x-s-common": x_s_common,
        "x-t": timestamp,
        "x-b3-traceid": generate_x_b3_traceid(),
        "x-xray-traceid": generate_x_xray_traceid(),
    }
    if "x-rap-param" in rap:
        result["x-rap-param"] = rap["x-rap-param"]

    return result
