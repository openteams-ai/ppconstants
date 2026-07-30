"""Unit conversion constants — ppconstants._units

The scipy.constants unit catalog: each constant is the number of SI base
units in one of the named unit (e.g. `mile` metres, `pound` kilograms).

Written as folded constant expressions over their defining relations
rather than as precomputed decimals, so the derivation chain is visible
in the source and the compiler does the arithmetic at compile time. The
chains mirror scipy's exactly, which makes the values bit-identical (a
precomputed literal would not be: `7000 * grain` is 0.45359236999999997,
not the 0.45359237 the avoirdupois pound is defined as).

Reference source: scipy.constants (verified bit-exact against 1.18.0),
whose values follow NIST SP 811 and the international yard-and-pound
agreement of 1959.
"""

from postyp import f64

from ppconstants._mathematical import pi
from ppconstants._physical import c, e, g

# ── Mass, in kilograms ──────────────────────────────────────────────────────

gram: f64 = 1e-3
metric_ton: f64 = 1e3
grain: f64 = 64.79891e-6
lb: f64 = 7000.0 * grain             # avoirdupois pound
pound = lb
blob: f64 = pound * g / 0.0254       # lbf*s^2/in
slinch = blob
slug: f64 = blob / 12.0              # lbf*s^2/ft
oz: f64 = pound / 16.0
ounce = oz
stone: f64 = 14.0 * pound
long_ton: f64 = 2240.0 * pound
short_ton: f64 = 2000.0 * pound
troy_ounce: f64 = 480.0 * grain      # only for metals / gems
troy_pound: f64 = 12.0 * troy_ounce
carat: f64 = 200e-6

# ── Angle, in radians ───────────────────────────────────────────────────────

degree: f64 = pi / 180.0
arcmin: f64 = degree / 60.0
arcminute = arcmin
arcsec: f64 = arcmin / 60.0
arcsecond = arcsec

# ── Time, in seconds ────────────────────────────────────────────────────────

minute: f64 = 60.0
hour: f64 = 60.0 * minute
day: f64 = 24.0 * hour
week: f64 = 7.0 * day
year: f64 = 365.0 * day
Julian_year: f64 = 365.25 * day

# ── Length, in metres ───────────────────────────────────────────────────────

inch: f64 = 0.0254
foot: f64 = 12.0 * inch
yard: f64 = 3.0 * foot
mile: f64 = 1760.0 * yard
mil: f64 = inch / 1000.0
pt: f64 = inch / 72.0                # typography point
point = pt
survey_foot: f64 = 1200.0 / 3937.0
survey_mile: f64 = 5280.0 * survey_foot
nautical_mile: f64 = 1852.0
fermi: f64 = 1e-15
angstrom: f64 = 1e-10
micron: f64 = 1e-6
au: f64 = 149597870700.0
astronomical_unit = au
light_year: f64 = Julian_year * c
parsec: f64 = au / arcsec

# ── Pressure, in pascals ────────────────────────────────────────────────────

atm: f64 = 101325.0                  # standard atmosphere (exact by definition)
atmosphere = atm
bar: f64 = 1e5
torr: f64 = atm / 760.0
mmHg = torr
psi: f64 = pound * g / (inch * inch)

# ── Area, in square metres ──────────────────────────────────────────────────

hectare: f64 = 1e4
acre: f64 = 43560.0 * (foot * foot)

# ── Volume, in cubic metres ─────────────────────────────────────────────────

litre: f64 = 1e-3
liter = litre
gallon: f64 = 231.0 * (inch * inch * inch)   # US liquid gallon
gallon_US = gallon
fluid_ounce: f64 = gallon / 128.0
fluid_ounce_US = fluid_ounce
bbl: f64 = 42.0 * gallon             # oil barrel
barrel = bbl
gallon_imp: f64 = 4.54609e-3         # UK
fluid_ounce_imp: f64 = gallon_imp / 160.0

# ── Speed, in metres per second ─────────────────────────────────────────────

kmh: f64 = 1e3 / hour
mph: f64 = mile / hour
mach: f64 = 340.5                    # approx. at 15 degrees C, 1 atm
speed_of_sound = mach
knot: f64 = nautical_mile / hour

# ── Temperature, in kelvin ──────────────────────────────────────────────────

zero_Celsius: f64 = 273.15
degree_Fahrenheit: f64 = 1.0 / 1.8   # only for temperature differences

# ── Energy, in joules ───────────────────────────────────────────────────────

eV: f64 = e                          # elementary_charge * 1 volt
electron_volt = eV
calorie_th: f64 = 4.184              # thermochemical calorie
calorie = calorie_th
calorie_IT: f64 = 4.1868             # international steam table calorie
erg: f64 = 1e-7
Btu_th: f64 = pound * degree_Fahrenheit * calorie_th / gram
Btu_IT: f64 = pound * degree_Fahrenheit * calorie_IT / gram
Btu = Btu_IT
ton_TNT: f64 = 1e9 * calorie_th

# ── Power, in watts ─────────────────────────────────────────────────────────

hp: f64 = 550.0 * foot * pound * g   # mechanical horsepower
horsepower = hp

# ── Force, in newtons ───────────────────────────────────────────────────────

dyn: f64 = 1e-5
dyne = dyn
lbf: f64 = pound * g
pound_force = lbf
kgf: f64 = g                         # kilogram-force
kilogram_force = kgf
