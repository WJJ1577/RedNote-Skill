# tests/test_cookies.py
import re
from rednote_core.crypto.cookie.a1_webid import generate_a1, generate_web_id
from rednote_core.crypto.cookie.gid import generate_gid


class TestA1:
    def test_length(self):
        a1 = generate_a1()
        assert len(a1) >= 32  # a1 is typically a hex string 32+ chars

    def test_format_hex(self):
        a1 = generate_a1()
        assert re.match(r"^[0-9a-f]+$", a1), f"a1 should be hex: {a1}"

    def test_unique(self):
        results = {generate_a1() for _ in range(10)}
        assert len(results) == 10  # All should be unique


class TestWebId:
    def test_format(self):
        web_id = generate_web_id()
        assert re.match(
            r"^[0-9a-f]{32}$", web_id
        ), f"webId format: {web_id}"

    def test_length(self):
        assert len(generate_web_id()) == 32

    def test_unique(self):
        results = {generate_web_id() for _ in range(10)}
        assert len(results) == 10


class TestGid:
    def test_format(self):
        gid = generate_gid()
        assert re.match(r"^[0-9a-f]+$", gid)

    def test_unique(self):
        results = {generate_gid() for _ in range(10)}
        assert len(results) == 10


from rednote_core.crypto.cookie.websectiga import generate_websectiga
from rednote_core.crypto.cookie.acw_tc import decrypt_acw_tc


class TestWebsectiga:
    def test_format(self):
        tig = generate_websectiga()
        assert isinstance(tig, str)
        assert len(tig) > 0

    def test_unique(self):
        results = {generate_websectiga() for _ in range(10)}
        assert len(results) == 10


class TestAcwTc:
    def test_decrypt_empty(self):
        result = decrypt_acw_tc("")
        assert result == ""
