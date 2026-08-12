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
Physical constants (_physical)        : exact SI (c, h, e, k, N_A),
                                        conventional (g), derived (hbar,
                                        R, sigma, Wien), CODATA 2022
                                        (mu_0, epsilon_0, G, alpha,
                                        Rydberg, m_e, m_p, m_n, m_u)
SI/binary prefixes (_prefixes)        : quetta ... quecto, kibi ... yobi
Unit catalog (_units)                 : mass, angle, time, length,
                                        pressure, area, volume, speed,
                                        temperature, energy, power, force
Conversion kernels (_conversions)     : lambda2nu, nu2lambda,
                                        convert_temperature
CODATA table (_codata)                : physical_constants, value, unit,
                                        precision, find, ConstantWarning

Everything above is compiled POST Python except `_codata`, which is
interpreted-only CPython-boundary code (spec §9.1) because POST Python
has no Str-keyed container yet. That divergence is documented in
`_codata` itself, in ROADMAP Target 5, and upstream in
`docs/upstream/03-str-keyed-containers.md`.
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
    # exact by convention
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

from ppconstants._units import (
    # mass
    gram, metric_ton, grain, lb, pound, blob, slinch, slug, oz, ounce,
    stone, long_ton, short_ton, troy_ounce, troy_pound, carat,
    # angle
    degree, arcmin, arcminute, arcsec, arcsecond,
    # time
    minute, hour, day, week, year, Julian_year,
    # length
    inch, foot, yard, mile, mil, pt, point, survey_foot, survey_mile,
    nautical_mile, fermi, angstrom, micron, au, astronomical_unit,
    light_year, parsec,
    # pressure
    atm, atmosphere, bar, torr, mmHg, psi,
    # area
    hectare, acre,
    # volume
    litre, liter, gallon, gallon_US, fluid_ounce, fluid_ounce_US,
    bbl, barrel, gallon_imp, fluid_ounce_imp,
    # speed
    kmh, mph, mach, speed_of_sound, knot,
    # temperature
    zero_Celsius, degree_Fahrenheit,
    # energy
    eV, electron_volt, calorie, calorie_th, calorie_IT, erg,
    Btu, Btu_IT, Btu_th, ton_TNT,
    # power
    hp, horsepower,
    # force
    dyn, dyne, lbf, pound_force, kgf, kilogram_force,
)

from ppconstants._conversions import (
    lambda2nu,
    nu2lambda,
    convert_temperature_code,
    CELSIUS, KELVIN, FAHRENHEIT, RANKINE,
)

# CPython-boundary import (spec §9.1): interpreted only, never compiled.
from ppconstants._codata import (
    physical_constants,
    value,
    unit,
    precision,
    find,
    ConstantWarning,
)

__all__ = [
    # ── mathematical ────────────────────────────────────────────────────
    "pi", "golden", "golden_ratio",
    # ── physical: exact (SI) ────────────────────────────────────────────
    "c", "speed_of_light", "h", "Planck", "e", "elementary_charge",
    "k", "Boltzmann", "N_A", "Avogadro",
    # ── physical: exact by convention ───────────────────────────────────
    "g",
    # ── physical: derived exact ─────────────────────────────────────────
    "hbar", "R", "gas_constant", "sigma", "Stefan_Boltzmann", "Wien",
    # ── physical: measured (CODATA 2022) ────────────────────────────────
    "mu_0", "epsilon_0", "G", "gravitational_constant",
    "alpha", "fine_structure", "Rydberg",
    "m_e", "electron_mass", "m_p", "proton_mass",
    "m_n", "neutron_mass", "m_u", "u", "atomic_mass",
    # ── SI decimal prefixes ─────────────────────────────────────────────
    "quetta", "ronna", "yotta", "zetta", "exa", "peta", "tera", "giga",
    "mega", "kilo", "hecto", "deka", "deci", "centi", "milli", "micro",
    "nano", "pico", "femto", "atto", "zepto", "yocto", "ronto", "quecto",
    # ── binary prefixes ─────────────────────────────────────────────────
    "kibi", "mebi", "gibi", "tebi", "pebi", "exbi", "zebi", "yobi",
    # ── units: mass ─────────────────────────────────────────────────────
    "gram", "metric_ton", "grain", "lb", "pound", "blob", "slinch",
    "slug", "oz", "ounce", "stone", "long_ton", "short_ton",
    "troy_ounce", "troy_pound", "carat",
    # ── units: angle ────────────────────────────────────────────────────
    "degree", "arcmin", "arcminute", "arcsec", "arcsecond",
    # ── units: time ─────────────────────────────────────────────────────
    "minute", "hour", "day", "week", "year", "Julian_year",
    # ── units: length ───────────────────────────────────────────────────
    "inch", "foot", "yard", "mile", "mil", "pt", "point", "survey_foot",
    "survey_mile", "nautical_mile", "fermi", "angstrom", "micron",
    "au", "astronomical_unit", "light_year", "parsec",
    # ── units: pressure ─────────────────────────────────────────────────
    "atm", "atmosphere", "bar", "torr", "mmHg", "psi",
    # ── units: area ─────────────────────────────────────────────────────
    "hectare", "acre",
    # ── units: volume ───────────────────────────────────────────────────
    "litre", "liter", "gallon", "gallon_US", "fluid_ounce",
    "fluid_ounce_US", "bbl", "barrel", "gallon_imp", "fluid_ounce_imp",
    # ── units: speed ────────────────────────────────────────────────────
    "kmh", "mph", "mach", "speed_of_sound", "knot",
    # ── units: temperature ──────────────────────────────────────────────
    "zero_Celsius", "degree_Fahrenheit",
    # ── units: energy ───────────────────────────────────────────────────
    "eV", "electron_volt", "calorie", "calorie_th", "calorie_IT", "erg",
    "Btu", "Btu_IT", "Btu_th", "ton_TNT",
    # ── units: power ────────────────────────────────────────────────────
    "hp", "horsepower",
    # ── units: force ────────────────────────────────────────────────────
    "dyn", "dyne", "lbf", "pound_force", "kgf", "kilogram_force",
    # ── conversion kernels ──────────────────────────────────────────────
    "lambda2nu", "nu2lambda",
    "convert_temperature", "convert_temperature_code",
    "CELSIUS", "KELVIN", "FAHRENHEIT", "RANKINE",
    # ── CODATA lookup table (interpreted only) ──────────────────────────
    "physical_constants", "value", "unit", "precision", "find",
    "ConstantWarning",
]

# ── scipy-compatible temperature API ───────────────────────────────────────
# CPython-boundary code (spec §9.1): the compiled artifact exposes the
# integer-code kernel; this wrapper only maps scale names to codes, which
# a compiled kernel cannot do today (see _conversions for why).

_SCALE_CODES = {
    "celsius": CELSIUS, "c": CELSIUS,
    "kelvin": KELVIN, "k": KELVIN,
    "fahrenheit": FAHRENHEIT, "f": FAHRENHEIT,
    "rankine": RANKINE, "r": RANKINE,
}


def _scale_code(scale, argname):
    try:
        return _SCALE_CODES[scale.lower()]
    except (AttributeError, KeyError):
        raise NotImplementedError(
            f"{argname}={scale!r} is unsupported: supported scales are "
            "Celsius, Kelvin, Fahrenheit, and Rankine"
        ) from None


def convert_temperature(val, old_scale, new_scale):
    """Convert `val` between the Celsius, Kelvin, Fahrenheit, and Rankine scales.

    Scale names follow scipy: 'Celsius'/'C', 'Kelvin'/'K',
    'Fahrenheit'/'F', 'Rankine'/'R', in any case. Delegates to the
    compiled `convert_temperature_code` ufunc, so `val` may be a scalar or
    any broadcastable array.
    """
    return convert_temperature_code(
        val,
        _scale_code(old_scale, "old_scale"),
        _scale_code(new_scale, "new_scale"),
    )


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
        # convert_temperature stays the interpreted string wrapper; it
        # picks up the native kernel through the global it calls.
        if name == "convert_temperature":
            continue
        if callable(globals()[name]) and hasattr(native, name):
            globals()[name] = getattr(native, name)
            replaced.append(name)

    if replaced:
        __native_available__ = True
        __native_module__ = native


_prefer_native()

del _prefer_native, _import_module
