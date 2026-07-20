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
Mathematical constants (_mathematical): pi, golden / golden_ratio
Physical constants (_physical)        : exact SI (c, h, e, k, N_A, g),
                                        derived (hbar, R, sigma, Wien),
                                        CODATA 2022 (mu_0, epsilon_0, G,
                                        alpha, Rydberg, m_e, m_p, m_n, m_u)
                                        plus scipy-compatible aliases
SI/binary prefixes (_prefixes)        : quetta ... quecto, kibi ... yobi
Conversion kernels (_conversions)     : lambda2nu, nu2lambda

Roadmap (see ROADMAP.md)
------------------------------
Unit catalog : mass, angle, time, length, pressure, area, volume,
               speed, temperature, energy, power, force
Kernels      : convert_temperature
CODATA table : physical_constants, value, unit, precision, find
               (blocked on Str-keyed containers upstream)
"""

from importlib import import_module as _import_module

from ppconstants._mathematical import (
    pi,
    golden,
    golden_ratio,  # alias for golden
)

from ppconstants._physical import (
    # exact (SI)
    c, speed_of_light,
    h, Planck,
    e, elementary_charge,
    k, Boltzmann,
    N_A, Avogadro,
    g,
    # derived exact
    hbar,
    R, gas_constant,
    sigma, Stefan_Boltzmann,
    Wien,
    # measured (CODATA 2022)
    mu_0, epsilon_0,
    G, gravitational_constant,
    alpha, fine_structure,
    Rydberg,
    m_e, electron_mass,
    m_p, proton_mass,
    m_n, neutron_mass,
    m_u, u, atomic_mass,
)

from ppconstants._prefixes import (
    quetta, ronna, yotta, zetta, exa, peta, tera, giga, mega, kilo,
    hecto, deka, deci, centi, milli, micro, nano, pico, femto, atto,
    zepto, yocto, ronto, quecto,
    kibi, mebi, gibi, tebi, pebi, exbi, zebi, yobi,
)

from ppconstants._conversions import (
    lambda2nu,
    nu2lambda,
)

__all__ = [
    # mathematical
    "pi", "golden", "golden_ratio",
    # physical: exact (SI)
    "c", "speed_of_light", "h", "Planck", "e", "elementary_charge",
    "k", "Boltzmann", "N_A", "Avogadro", "g",
    # physical: derived exact
    "hbar", "R", "gas_constant", "sigma", "Stefan_Boltzmann", "Wien",
    # physical: measured (CODATA 2022)
    "mu_0", "epsilon_0", "G", "gravitational_constant",
    "alpha", "fine_structure", "Rydberg",
    "m_e", "electron_mass", "m_p", "proton_mass",
    "m_n", "neutron_mass", "m_u", "u", "atomic_mass",
    # SI decimal prefixes
    "quetta", "ronna", "yotta", "zetta", "exa", "peta", "tera", "giga",
    "mega", "kilo", "hecto", "deka", "deci", "centi", "milli", "micro",
    "nano", "pico", "femto", "atto", "zepto", "yocto", "ronto", "quecto",
    # binary prefixes
    "kibi", "mebi", "gibi", "tebi", "pebi", "exbi", "zebi", "yobi",
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
