"""Conversion kernels — ppconstants._conversions

Public API
----------
lambda2nu(lambda_)                      — wavelength [m] -> frequency [Hz]
nu2lambda(nu)                           — frequency [Hz] -> wavelength [m]
convert_temperature_code(val, old, new) — temperature scale conversion,
                                          scales given as integer codes

lambda2nu/nu2lambda are exact relations through the SI-defined speed of
light (nu = c / lambda), imported as a cross-module constant from
ppconstants._physical.

Why integer scale codes
-----------------------
scipy spells the temperature scales as strings. A `Str` parameter is
accepted by the checker and appears to compile, but the reference
compiler currently lowers a string literal to `int64_t 0` and emits a
pointer-vs-integer comparison, so `scale == "C"` is always false in
compiled code while interpreted mode is correct — a silent wrong answer
(filed upstream; see ROADMAP Target 3). Integer codes are ordinary scalar
dtypes that lower correctly, so the compiled kernel takes codes and the
scipy-compatible string API is a thin interpreted wrapper in
`ppconstants/__init__.py`.

Invalid codes are rejected by that wrapper, not by the kernel: a compiled
kernel has no way to signal a domain error yet (returning `NAN` fails to
lower, postpython#36), so the kernel treats an unrecognised code as
"already kelvin" and C-ABI consumers must pass valid codes.
"""

from postyp import f64, i64
from postpyc import vectorize

from ppconstants._physical import c
from ppconstants._units import zero_Celsius

# Scale codes accepted by convert_temperature_code.
CELSIUS: i64 = 0
KELVIN: i64 = 1
FAHRENHEIT: i64 = 2
RANKINE: i64 = 3


@vectorize
def lambda2nu(lambda_: f64) -> f64:
    """Convert wavelength in metres to optical frequency in Hz: nu = c / lambda."""
    return c / lambda_


@vectorize
def nu2lambda(nu: f64) -> f64:
    """Convert optical frequency in Hz to wavelength in metres: lambda = c / nu."""
    return c / nu


@vectorize
def convert_temperature_code(val: f64, old_code: i64, new_code: i64) -> f64:
    """Convert `val` between temperature scales given as integer codes.

    Codes are CELSIUS, KELVIN, FAHRENHEIT, RANKINE. Conversion goes
    through kelvin, matching scipy's arithmetic step for step so results
    agree bit for bit.
    """
    kelvin: f64 = val
    if old_code == CELSIUS:
        kelvin = val + zero_Celsius
    elif old_code == FAHRENHEIT:
        kelvin = (val - 32.0) * 5.0 / 9.0 + zero_Celsius
    elif old_code == RANKINE:
        kelvin = val * 5.0 / 9.0

    if new_code == CELSIUS:
        return kelvin - zero_Celsius
    elif new_code == FAHRENHEIT:
        return (kelvin - zero_Celsius) * 9.0 / 5.0 + 32.0
    elif new_code == RANKINE:
        return kelvin * 9.0 / 5.0
    return kelvin
