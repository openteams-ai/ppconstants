"""Conversion kernels — ppconstants._conversions

Public API
----------
lambda2nu(lambda_) — convert wavelength [m] to optical frequency [Hz]
nu2lambda(nu)      — convert optical frequency [Hz] to wavelength [m]

Both are exact relations through the SI-defined speed of light
(nu = c / lambda), imported as a cross-module constant from
ppconstants._physical. convert_temperature is tracked in ROADMAP Target 3.
"""

from postyp import f64
from postpyc import vectorize

from ppconstants._physical import c


@vectorize
def lambda2nu(lambda_: f64) -> f64:
    """Convert wavelength in metres to optical frequency in Hz: nu = c / lambda."""
    return c / lambda_


@vectorize
def nu2lambda(nu: f64) -> f64:
    """Convert optical frequency in Hz to wavelength in metres: lambda = c / nu."""
    return c / nu
