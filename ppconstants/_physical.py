"""Physical constants — ppconstants._physical

Scalar physical constants as module-level typed POST Python constants,
mirroring the scipy.constants scalar table (names and aliases match).

Reference sources
-----------------
- "exact (SI)": exact by the 2019 SI redefinition (BIPM 9th SI brochure).
- "derived exact": folded constant expressions over exact values.
- "CODATA 2022": measured values from the CODATA 2022 adjustment, as
  published in scipy.constants (verified against scipy 1.18.0).
"""

from postyp import f64
from postpyc.math import PI

# ── Exact by SI definition (2019 redefinition) ──────────────────────────────

c: f64 = 299792458.0                 # speed of light in vacuum [m/s]
speed_of_light = c
h: f64 = 6.62607015e-34              # Planck constant [J s]
Planck = h
e: f64 = 1.602176634e-19             # elementary charge [C]
elementary_charge = e
k: f64 = 1.380649e-23                # Boltzmann constant [J/K]
Boltzmann = k
N_A: f64 = 6.02214076e23             # Avogadro constant [1/mol]
Avogadro = N_A
g: f64 = 9.80665                     # standard acceleration of gravity [m/s^2]

# ── Derived exact (folded constant expressions) ─────────────────────────────

hbar: f64 = h / (2.0 * PI)           # reduced Planck constant [J s]
R: f64 = N_A * k                     # molar gas constant [J/(mol K)]
gas_constant = R

# ── Derived exact, precomputed ──────────────────────────────────────────────
# Closed forms need non-foldable operations (higher powers, root finding);
# values are the full-precision float64 results as published by scipy.

sigma: f64 = 5.6703744191844314e-08  # Stefan-Boltzmann: 2 pi^5 k^4 / (15 h^3 c^2)
Stefan_Boltzmann = sigma
Wien: f64 = 0.0028977719551851727    # Wien wavelength displacement law constant

# ── Measured (CODATA 2022) ──────────────────────────────────────────────────

mu_0: f64 = 1.25663706127e-06        # vacuum magnetic permeability [N/A^2]
epsilon_0: f64 = 8.8541878188e-12    # vacuum electric permittivity [F/m]
G: f64 = 6.6743e-11                  # Newtonian constant of gravitation [m^3/(kg s^2)]
gravitational_constant = G
alpha: f64 = 0.0072973525643         # fine-structure constant [1]
fine_structure = alpha
Rydberg: f64 = 10973731.568157       # Rydberg constant [1/m]
m_e: f64 = 9.1093837139e-31          # electron mass [kg]
electron_mass = m_e
m_p: f64 = 1.67262192595e-27         # proton mass [kg]
proton_mass = m_p
m_n: f64 = 1.67492750056e-27         # neutron mass [kg]
neutron_mass = m_n
m_u: f64 = 1.66053906892e-27         # atomic mass constant [kg]
u = m_u
atomic_mass = m_u
