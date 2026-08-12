"""POST compile entry for ppconstants (spec §9.1).

`__init__.py` is the Python namespace manifest: it re-exports everything
users import, *including* `_codata`, which is interpreted-only
CPython-boundary code (POST Python has no Str-keyed container yet). A
compiler pointed at `__init__.py` would try to compile `_codata` as POST
source and fail.

This module is the compiler's entry point instead. It re-exports exactly
the POST translation units, so the compiled artifact contains the kernels
and their folded constants and nothing else. Spec §9.1: "A package may
instead provide an explicit compile entry named `__post__.py` ... When a
compiler is asked to build a package directory, `__post__.py` takes
precedence over the `__init__.py` manifest."

Note that the precedence rule is keyed on being handed the *directory*.
Build scripts and tests therefore pass `ppconstants/`, not
`ppconstants/__init__.py`.
"""

from ppconstants._mathematical import (
    pi,
    golden,
    golden_ratio,
)

from ppconstants._physical import (
    c, speed_of_light,
    h, Planck,
    e, elementary_charge,
    k, Boltzmann,
    N_A, Avogadro,
    g,
    hbar,
    R, gas_constant,
    sigma, Stefan_Boltzmann,
    Wien,
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
    gram, metric_ton, grain, lb, pound, blob, slinch, slug, oz, ounce,
    stone, long_ton, short_ton, troy_ounce, troy_pound, carat,
    degree, arcmin, arcminute, arcsec, arcsecond,
    minute, hour, day, week, year, Julian_year,
    inch, foot, yard, mile, mil, pt, point, survey_foot, survey_mile,
    nautical_mile, fermi, angstrom, micron, au, astronomical_unit,
    light_year, parsec,
    atm, atmosphere, bar, torr, mmHg, psi,
    hectare, acre,
    litre, liter, gallon, gallon_US, fluid_ounce, fluid_ounce_US,
    bbl, barrel, gallon_imp, fluid_ounce_imp,
    kmh, mph, mach, speed_of_sound, knot,
    zero_Celsius, degree_Fahrenheit,
    eV, electron_volt, calorie, calorie_th, calorie_IT, erg,
    Btu, Btu_IT, Btu_th, ton_TNT,
    hp, horsepower,
    dyn, dyne, lbf, pound_force, kgf, kilogram_force,
)

from ppconstants._conversions import (
    lambda2nu,
    nu2lambda,
    convert_temperature_code,
    CELSIUS, KELVIN, FAHRENHEIT, RANKINE,
)

__all__ = [
    "lambda2nu",
    "nu2lambda",
    "convert_temperature_code",
]
