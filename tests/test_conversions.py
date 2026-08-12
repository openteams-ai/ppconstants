"""Interpreted-mode tests for the conversion kernels.

Reference values are exact through the SI-defined speed of light
(c = 299792458 m/s); no scipy required.
"""

import pytest

# Import from the defining modules, not the package: ppconstants/__init__
# swaps in native ufuncs when ppconstants_native is importable, and these
# tests must always exercise the interpreted kernels.
from ppconstants._conversions import lambda2nu, nu2lambda
from ppconstants._physical import c


def close(a, b, rtol=1e-15):
    return abs(a - b) <= rtol * abs(b)


class TestLambda2Nu:
    def test_one_metre(self):
        assert lambda2nu(1.0) == c

    def test_visible_green(self):
        # 532 nm doubled Nd:YAG line: nu = c / 532e-9 Hz, exact division.
        assert close(lambda2nu(532e-9), 299792458.0 / 532e-9)

    def test_reciprocal_relation(self):
        for lam in [1e-9, 632.8e-9, 1.0, 21.106e-2]:
            assert close(nu2lambda(lambda2nu(lam)), lam)

    def test_roundtrip_across_27_decades(self):
        # Backs the range quoted in docs/accuracy.md; runs without numpy.
        lam = 1e-12
        while lam <= 1e15:
            assert close(nu2lambda(lambda2nu(lam)), lam), lam
            lam *= 10.0


class TestNu2Lambda:
    def test_one_hertz(self):
        assert nu2lambda(1.0) == c

    def test_hydrogen_line(self):
        # 1420.405751768 MHz hydrogen line -> ~21.106 cm (c / nu, full float64).
        assert close(nu2lambda(1420.405751768e6), 0.211061140541598)

    def test_roundtrip(self):
        for nu in [1.0, 1e6, 4.74e14, 3e18]:
            assert close(lambda2nu(nu2lambda(nu)), nu)


class TestBroadcasting:
    def test_numpy_arrays(self):
        np = pytest.importorskip("numpy")
        lam = np.array([1.0, 2.0, 4.0])
        out = lambda2nu(lam)
        assert np.allclose(out, np.array([c, c / 2.0, c / 4.0]), rtol=1e-15)
        back = nu2lambda(out)
        assert np.allclose(back, lam, rtol=1e-15)
