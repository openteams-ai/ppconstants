"""Plain C ABI shared-library smoke tests.

Loads the package shared library with ctypes and calls exported C
functions directly, without importing a CPython extension module or the
NumPy ufunc layer. Constants do not yet appear in the C ABI (header or
manifest) — see ROADMAP "Upstream request backlog"; these tests verify
that they fold correctly into the exported kernels instead.
"""

from __future__ import annotations

import ctypes
import json
import shutil
from pathlib import Path

import pytest

import ppconstants

cc = shutil.which("cc") or shutil.which("clang") or shutil.which("gcc")

pytestmark = pytest.mark.skipif(cc is None, reason="No C compiler available")


@pytest.fixture(scope="module")
def native_artifact(tmp_path_factory):
    from postpyc.build import build_file

    out_dir = tmp_path_factory.mktemp("ppconstants-native-abi")
    lib_path = build_file(
        Path(ppconstants.__file__),
        output=out_dir / "ppconstants.so",
        emit_header=True,
        emit_manifest=True,
    )
    return {
        "path": lib_path,
        "lib": ctypes.CDLL(str(lib_path)),
        "header": lib_path.with_suffix(".h").read_text(),
        "manifest": json.loads(lib_path.with_suffix(".json").read_text()),
    }


def _bind(lib, export_name: str):
    """Bind a source-level POST export through its stable pp_* C symbol."""
    fn = getattr(lib, f"pp_{export_name}")
    fn.argtypes = [ctypes.c_double]
    fn.restype = ctypes.c_double
    return fn


def test_lambda2nu_folds_speed_of_light(native_artifact):
    lambda2nu = _bind(native_artifact["lib"], "lambda2nu")
    assert lambda2nu(1.0) == 299792458.0


def test_nu2lambda_roundtrip(native_artifact):
    lambda2nu = _bind(native_artifact["lib"], "lambda2nu")
    nu2lambda = _bind(native_artifact["lib"], "nu2lambda")
    lam = 632.8e-9
    assert abs(nu2lambda(lambda2nu(lam)) - lam) <= 1e-15 * lam


def test_convert_temperature_code_through_c_abi(native_artifact):
    fn = getattr(native_artifact["lib"], "pp_convert_temperature_code")
    fn.argtypes = [ctypes.c_double, ctypes.c_int64, ctypes.c_int64]
    fn.restype = ctypes.c_double
    assert fn(0.0, 0, 1) == 273.15          # 0 C  -> K
    assert fn(0.0, 0, 2) == 32.0            # 0 C  -> F
    assert fn(-40.0, 2, 0) == -40.0         # -40 F -> C


def test_header_declares_kernel_exports(native_artifact):
    header = native_artifact["header"]
    assert "double pp_lambda2nu(double" in header
    assert "double pp_nu2lambda(double" in header
    assert "double pp_convert_temperature_code(double" in header


def test_constants_absent_from_c_abi(native_artifact):
    """Regression pin for the gap filed upstream (ROADMAP Target 6).

    Module-level constants fold into kernels but are not exported: no
    pp_* symbol, no header declaration, no manifest entry. When the
    compiler grows constant exports this test should start failing and be
    inverted — that failure is the signal to update the roadmap.
    """
    header = native_artifact["header"]
    manifest_names = {e["name"] for e in native_artifact["manifest"]["exports"]}
    for constant in ("c", "pi", "zero_Celsius", "kilo"):
        assert constant not in manifest_names
        # Match a declaration, not a prefix of a longer export name.
        assert f"pp_{constant}(" not in header
        assert f"pp_{constant};" not in header


def test_manifest_lists_kernel_exports(native_artifact):
    manifest = native_artifact["manifest"]
    exports = {e["name"]: e for e in manifest["exports"]}
    for name in ("lambda2nu", "nu2lambda"):
        assert name in exports
        assert exports[name]["c_symbol"] == f"pp_{name}"
