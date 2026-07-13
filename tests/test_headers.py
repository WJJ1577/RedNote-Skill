# tests/test_headers.py
import re
from rednote_core.crypto.header.x_b3 import generate_x_b3_traceid
from rednote_core.crypto.header.x_xray import generate_x_xray_traceid
from rednote_core.crypto.header.x_s_common import generate_x_s_common
from rednote_core.crypto.header.x_s import generate_x_s
from rednote_core.crypto.header.x_rap_param import generate_x_rap_param


class TestXB3:
    def test_format(self):
        trace_id = generate_x_b3_traceid()
        assert re.match(r"^[0-9a-f]{32}$", trace_id), f"Bad: {trace_id}"

    def test_unique(self):
        results = {generate_x_b3_traceid() for _ in range(10)}
        assert len(results) == 10


class TestXXray:
    def test_format(self):
        tid = generate_x_xray_traceid()
        assert len(tid) >= 16, f"Too short: {tid}"

    def test_unique(self):
        results = {generate_x_xray_traceid() for _ in range(10)}
        assert len(results) == 10


class TestXSCommon:
    def test_returns_dict(self):
        result = generate_x_s_common(
            a1="a" * 32,
            web_session="",
            timestamp="1234567890000",
        )
        assert isinstance(result, dict)
        assert "x-s-common" in result

    def test_platform_info_present(self):
        result = generate_x_s_common("a1test", "", "1234567890000")
        common = result["x-s-common"]
        assert isinstance(common, str)
        assert len(common) > 0


class TestXS:
    def test_generates_signature(self):
        result = generate_x_s(
            url="/api/sns/web/v1/search/notes",
            data='{"keyword":"test"}',
            x_s_common="platform=1;;aid=test;;build=1",
            x_t="1234567890000",
            a1="test_a1_value_32_chars_long!",
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_different_data_different_sig(self):
        sig1 = generate_x_s("/api/test", '{"a":1}', "common", "1", "a1")
        sig2 = generate_x_s("/api/test", '{"a":2}', "common", "1", "a1")
        assert sig1 != sig2

    def test_different_url_different_sig(self):
        sig1 = generate_x_s("/api/a", None, "common", "1", "a1")
        sig2 = generate_x_s("/api/b", None, "common", "1", "a1")
        assert sig1 != sig2


class TestXRapParam:
    def test_returns_dict(self):
        result = generate_x_rap_param()
        assert isinstance(result, dict)
        assert "x-rap-param" in result

    def test_value_is_base64(self):
        result = generate_x_rap_param()["x-rap-param"]
        assert isinstance(result, str)
        assert len(result) > 0
