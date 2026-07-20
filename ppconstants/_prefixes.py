"""SI and binary prefixes — ppconstants._prefixes

Module-level typed POST Python constants mirroring scipy.constants.

Intentional divergence from scipy: binary prefixes are Float64, not
Python int (scipy returns int). POST constants are fixed-width, and
`zebi`/`yobi` exceed Int64 range; every power of two here is exactly
representable in float64, so values are numerically identical.
"""

from postyp import f64

# ── SI decimal prefixes ─────────────────────────────────────────────────────

quetta: f64 = 1e30
ronna: f64 = 1e27
yotta: f64 = 1e24
zetta: f64 = 1e21
exa: f64 = 1e18
peta: f64 = 1e15
tera: f64 = 1e12
giga: f64 = 1e9
mega: f64 = 1e6
kilo: f64 = 1e3
hecto: f64 = 1e2
deka: f64 = 1e1
deci: f64 = 1e-1
centi: f64 = 1e-2
milli: f64 = 1e-3
micro: f64 = 1e-6
nano: f64 = 1e-9
pico: f64 = 1e-12
femto: f64 = 1e-15
atto: f64 = 1e-18
zepto: f64 = 1e-21
yocto: f64 = 1e-24
ronto: f64 = 1e-27
quecto: f64 = 1e-30

# ── Binary prefixes ─────────────────────────────────────────────────────────

kibi: f64 = 2.0 ** 10
mebi: f64 = 2.0 ** 20
gibi: f64 = 2.0 ** 30
tebi: f64 = 2.0 ** 40
pebi: f64 = 2.0 ** 50
exbi: f64 = 2.0 ** 60
zebi: f64 = 2.0 ** 70
yobi: f64 = 2.0 ** 80
