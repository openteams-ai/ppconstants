"""Interpreted-mode tests for SI decimal and binary prefixes."""

import ppconstants as ppc

DECIMAL = {
    "quetta": 1e30, "ronna": 1e27, "yotta": 1e24, "zetta": 1e21,
    "exa": 1e18, "peta": 1e15, "tera": 1e12, "giga": 1e9,
    "mega": 1e6, "kilo": 1e3, "hecto": 1e2, "deka": 1e1,
    "deci": 1e-1, "centi": 1e-2, "milli": 1e-3, "micro": 1e-6,
    "nano": 1e-9, "pico": 1e-12, "femto": 1e-15, "atto": 1e-18,
    "zepto": 1e-21, "yocto": 1e-24, "ronto": 1e-27, "quecto": 1e-30,
}

BINARY = {
    "kibi": 2 ** 10, "mebi": 2 ** 20, "gibi": 2 ** 30, "tebi": 2 ** 40,
    "pebi": 2 ** 50, "exbi": 2 ** 60, "zebi": 2 ** 70, "yobi": 2 ** 80,
}


def test_decimal_values():
    for name, value in DECIMAL.items():
        assert getattr(ppc, name) == value, name


def test_binary_values_exact_powers_of_two():
    # Float64 divergence from scipy's int is intentional (see _prefixes);
    # every power of two is exactly representable, so == holds.
    for name, value in BINARY.items():
        assert getattr(ppc, name) == value, name


def test_reciprocal_pairs():
    pairs = [
        ("quetta", "quecto"), ("ronna", "ronto"), ("yotta", "yocto"),
        ("zetta", "zepto"), ("exa", "atto"), ("peta", "femto"),
        ("tera", "pico"), ("giga", "nano"), ("mega", "micro"),
        ("kilo", "milli"), ("hecto", "centi"), ("deka", "deci"),
    ]
    for big, small in pairs:
        product = getattr(ppc, big) * getattr(ppc, small)
        assert abs(product - 1.0) < 1e-9, (big, small)


def test_binary_ladder():
    ladder = ["kibi", "mebi", "gibi", "tebi", "pebi", "exbi", "zebi", "yobi"]
    for lower, upper in zip(ladder, ladder[1:]):
        assert getattr(ppc, upper) == getattr(ppc, lower) * 1024.0
