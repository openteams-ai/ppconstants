"""Interpreted-mode tests for scalar constants."""

from ppconstants import c, speed_of_light


class TestSpeedOfLight:
    def test_exact_si_value(self):
        # Exact by the 2019 SI definition of the metre.
        assert c == 299792458.0

    def test_alias_identity(self):
        assert speed_of_light == c

    def test_type(self):
        assert isinstance(c, float)
