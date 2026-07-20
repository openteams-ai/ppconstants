"""Compiled NumPy extension vs. interpreted mode.

Builds ppconstants as a CPython extension module once per session, then
verifies that every registered ufunc agrees with the interpreted POST
Python implementation, including array broadcasting behavior.
"""

import importlib.util
import shutil

import pytest

np = pytest.importorskip("numpy")

import ppconstants
# The interpreted reference comes from the defining module, never the
# package namespace, which may itself be native-backed at import time.
from ppconstants import _conversions

cc = shutil.which("cc") or shutil.which("clang") or shutil.which("gcc")

pytestmark = pytest.mark.skipif(cc is None, reason="No C compiler available")


@pytest.fixture(scope="module")
def native(tmp_path_factory):
    from pathlib import Path

    from postpyc.build import build_file

    out_dir = tmp_path_factory.mktemp("ppconstants-ext")
    ext = build_file(
        Path(ppconstants.__file__),
        ext_module=True,
        module_name="ppconstants_native_test",
        output=out_dir / "ppconstants_native_test.so",
    )
    spec = importlib.util.spec_from_file_location("ppconstants_native_test", str(ext))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_all_public_ufuncs_registered(native):
    registered = {n for n in dir(native) if not n.startswith("_")}
    expected = {"lambda2nu", "nu2lambda"}
    assert expected <= registered
    for name in expected:
        assert isinstance(getattr(native, name), np.ufunc), name


@pytest.mark.parametrize("name", ["lambda2nu", "nu2lambda"])
def test_compiled_matches_interpreted(native, name):
    x = np.logspace(-9.0, 3.0, 25)
    compiled = getattr(native, name)(x)
    interpreted = getattr(_conversions, name)(x)
    assert np.allclose(compiled, interpreted, rtol=1e-15)


def test_broadcasting_and_out(native):
    x = np.array([[1.0, 2.0], [4.0, 8.0]])
    out = np.empty_like(x)
    result = native.lambda2nu(x, out=out)
    assert result is out
    assert np.allclose(out, 299792458.0 / x, rtol=1e-15)
