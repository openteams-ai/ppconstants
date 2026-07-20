"""Optional scipy comparison sweep.

scipy is a reference, never a dependency: this module is skipped when
scipy is not installed. Every public constant shared with scipy.constants
must match exactly (binary prefixes compare int == float, which is exact
for powers of two). Kernels are compared pointwise.
"""

import pytest

scipy_constants = pytest.importorskip("scipy.constants")

import ppconstants as ppc


def _shared_constant_names():
    return [
        name for name in ppc.__all__
        if not callable(getattr(ppc, name)) and hasattr(scipy_constants, name)
    ]


def test_every_constant_has_a_scipy_counterpart():
    missing = [
        name for name in ppc.__all__
        if not callable(getattr(ppc, name)) and not hasattr(scipy_constants, name)
    ]
    assert missing == []


@pytest.mark.parametrize("name", _shared_constant_names())
def test_constant_matches_scipy(name):
    assert getattr(ppc, name) == getattr(scipy_constants, name)


@pytest.mark.parametrize("name", ["lambda2nu", "nu2lambda"])
def test_kernel_matches_scipy(name):
    ours = getattr(ppc, name)
    theirs = getattr(scipy_constants, name)
    for x in (1e-9, 532e-9, 1.0, 1.42040575e9, 4.74e14):
        assert ours(x) == theirs(x)
