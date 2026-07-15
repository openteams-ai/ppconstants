"""Default import behavior for optional native acceleration."""

import subprocess
import sys
import textwrap


def test_package_import_prefers_available_native_module():
    script = textwrap.dedent(
        """
        import sys
        import types

        native = types.ModuleType("ppconstants_native")
        native.lambda2nu = lambda x: "native-lambda2nu"
        sys.modules["ppconstants_native"] = native

        import ppconstants

        assert ppconstants.__native_available__ is True
        assert ppconstants.__native_module__ is native
        assert ppconstants.lambda2nu(1.0) == "native-lambda2nu"
        # Constants are never replaced by the extension.
        assert ppconstants.c == 299792458.0
        # Kernels absent from the extension keep the interpreted fallback.
        assert abs(ppconstants.nu2lambda(1.0) - 299792458.0) == 0.0
        """
    )

    subprocess.run([sys.executable, "-c", script], check=True)
