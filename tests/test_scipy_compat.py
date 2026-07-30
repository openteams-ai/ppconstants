"""Optional scipy comparison sweep.

scipy is a reference, never a dependency: this module is skipped when
scipy is not installed. Every public constant shared with scipy.constants
must match exactly (binary prefixes compare int == float, which is exact
for powers of two). Kernels are compared pointwise.

Exact equality is deliberate, not an oversight: values were sourced from
scipy 1.18.0 (CODATA 2022), and a mismatch against a newer scipy signals
reference drift (e.g. a future CODATA adjustment) that must be reconciled
deliberately, source and tests together — never papered over with a
tolerance.
"""

import pytest

scipy_constants = pytest.importorskip("scipy.constants")

import ppconstants as ppc

# Public names with no scipy counterpart by design: the integer scale
# codes exist because a compiled kernel cannot take string scale names
# (see ppconstants/_conversions.py).
NOT_IN_SCIPY = {"CELSIUS", "KELVIN", "FAHRENHEIT", "RANKINE",
                "convert_temperature_code"}


def _constant_names():
    return [
        name for name in ppc.__all__
        if name not in NOT_IN_SCIPY and not callable(getattr(ppc, name))
    ]


def test_every_constant_has_a_scipy_counterpart():
    missing = [
        name for name in _constant_names()
        if not hasattr(scipy_constants, name)
    ]
    assert missing == []


def test_sweep_is_not_trivially_empty():
    # Guards against the sweep silently degenerating to zero cases.
    assert len(_constant_names()) > 100


@pytest.mark.parametrize("name", _constant_names())
def test_constant_matches_scipy(name):
    assert getattr(ppc, name) == getattr(scipy_constants, name)


@pytest.mark.parametrize("name", ["lambda2nu", "nu2lambda"])
def test_kernel_matches_scipy(name):
    ours = getattr(ppc, name)
    theirs = getattr(scipy_constants, name)
    for x in (1e-9, 532e-9, 1.0, 1.42040575e9, 4.74e14):
        assert ours(x) == theirs(x)


@pytest.mark.parametrize(
    "old,new",
    [(a, b)
     for a in ("Celsius", "Kelvin", "Fahrenheit", "Rankine")
     for b in ("Celsius", "Kelvin", "Fahrenheit", "Rankine")],
)
def test_convert_temperature_matches_scipy(old, new):
    for val in (-273.15, -40.0, 0.0, 37.0, 100.0, 1000.0):
        ours = ppc.convert_temperature(val, old, new)
        theirs = scipy_constants.convert_temperature(val, old, new)
        assert ours == pytest.approx(theirs, rel=0, abs=1e-12), (val, old, new)
