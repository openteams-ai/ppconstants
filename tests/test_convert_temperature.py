"""Tests for temperature conversion (kernel and scipy-compatible wrapper).

Reference points are physical definitions, not scipy outputs: water's
freezing and boiling points, absolute zero, and the Fahrenheit/Celsius
crossover at -40.
"""

import pytest

import ppconstants as ppc
# The interpreted kernel, never the possibly-native package attribute.
from ppconstants._conversions import convert_temperature_code


def close(a, b, atol=1e-10):
    return abs(a - b) <= atol


class TestKernelCodes:
    def test_celsius_to_kelvin(self):
        assert close(convert_temperature_code(0.0, ppc.CELSIUS, ppc.KELVIN), 273.15)
        assert close(convert_temperature_code(100.0, ppc.CELSIUS, ppc.KELVIN), 373.15)

    def test_kelvin_to_celsius(self):
        assert close(convert_temperature_code(273.15, ppc.KELVIN, ppc.CELSIUS), 0.0)

    def test_identity_for_each_scale(self):
        for code in (ppc.CELSIUS, ppc.KELVIN, ppc.FAHRENHEIT, ppc.RANKINE):
            assert close(convert_temperature_code(42.0, code, code), 42.0)

    def test_rankine_is_absolute(self):
        # 0 R is absolute zero, i.e. -273.15 C.
        assert close(convert_temperature_code(0.0, ppc.RANKINE, ppc.CELSIUS), -273.15)
        assert close(convert_temperature_code(0.0, ppc.KELVIN, ppc.RANKINE), 0.0)


class TestStringWrapper:
    def test_water_freezing_and_boiling(self):
        assert close(ppc.convert_temperature(0.0, "Celsius", "Fahrenheit"), 32.0)
        assert close(ppc.convert_temperature(100.0, "Celsius", "Fahrenheit"), 212.0)

    def test_fahrenheit_celsius_crossover(self):
        assert close(ppc.convert_temperature(-40.0, "F", "C"), -40.0)

    def test_absolute_zero(self):
        assert close(ppc.convert_temperature(0.0, "Kelvin", "Celsius"), -273.15)
        assert close(ppc.convert_temperature(0.0, "K", "R"), 0.0)
        assert close(
            ppc.convert_temperature(0.0, "Rankine", "Fahrenheit"), -459.67, atol=1e-8
        )

    def test_scale_names_are_case_insensitive(self):
        variants = ["Celsius", "celsius", "C", "c"]
        expected = ppc.convert_temperature(25.0, "Celsius", "Kelvin")
        for name in variants:
            assert close(ppc.convert_temperature(25.0, name, "Kelvin"), expected)

    def test_roundtrip_all_pairs(self):
        scales = ["Celsius", "Kelvin", "Fahrenheit", "Rankine"]
        for a in scales:
            for b in scales:
                there = ppc.convert_temperature(37.0, a, b)
                back = ppc.convert_temperature(there, b, a)
                assert close(back, 37.0, atol=1e-9), (a, b)

    def test_unsupported_scale_raises(self):
        with pytest.raises(NotImplementedError, match="old_scale"):
            ppc.convert_temperature(0.0, "Reaumur", "Celsius")
        with pytest.raises(NotImplementedError, match="new_scale"):
            ppc.convert_temperature(0.0, "Celsius", "Reaumur")

    def test_non_string_scale_raises(self):
        with pytest.raises(NotImplementedError):
            ppc.convert_temperature(0.0, 0, "Celsius")


class TestArrayBroadcasting:
    def test_numpy_array(self):
        np = pytest.importorskip("numpy")
        celsius = np.array([-40.0, 0.0, 37.0, 100.0])
        fahrenheit = ppc.convert_temperature(celsius, "C", "F")
        assert np.allclose(fahrenheit, np.array([-40.0, 32.0, 98.6, 212.0]))
