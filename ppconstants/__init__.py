"""ppconstants — POST Python reimplementation of scipy.constants.

Scalar constants are module-level typed POST Python constants; conversion
functions are @vectorize kernels. The postpyc compiler lowers the kernels
to native shared-library code and folds the constants into them; in
interpreted mode everything runs under plain CPython. When the optional
`ppconstants_native` extension module is installed next to this package,
matching public functions are replaced with native NumPy ufuncs at import
time (constants always come from this source package).

Implemented
------------------------------
Physical constants (_physical)   : c / speed_of_light
Conversion kernels (_conversions): lambda2nu, nu2lambda

Roadmap (see ROADMAP.md)
------------------------------
Mathematical constants : pi, golden, golden_ratio
Physical constants     : h, hbar, G, g, e, R, alpha, N_A, k, sigma, Wien,
                         Rydberg, m_e, m_p, m_n, mu_0, epsilon_0, ...
SI prefixes            : quetta ... quecto, kibi ... yobi
Unit catalog           : mass, angle, time, length, pressure, area, volume,
                         speed, temperature, energy, power, force
Kernels                : convert_temperature
CODATA table           : physical_constants, value, unit, precision, find
                         (blocked on Str-keyed containers upstream)
"""

from importlib import import_module as _import_module

from ppconstants._physical import (
    c,
    speed_of_light,  # alias for c
)

from ppconstants._conversions import (
    lambda2nu,
    nu2lambda,
)

__all__ = [
    # physical
    "c", "speed_of_light",
    # conversions
    "lambda2nu", "nu2lambda",
]

__native_available__ = False
__native_module__ = None


def _prefer_native() -> None:
    """Prefer compiled ufuncs when a sibling native extension is installed."""
    global __native_available__, __native_module__

    try:
        native = _import_module("ppconstants_native")
    except ModuleNotFoundError as exc:
        if exc.name == "ppconstants_native":
            return
        raise

    replaced = []
    for name in __all__:
        if callable(globals()[name]) and hasattr(native, name):
            globals()[name] = getattr(native, name)
            replaced.append(name)

    if replaced:
        __native_available__ = True
        __native_module__ = native


_prefer_native()

del _prefer_native, _import_module
