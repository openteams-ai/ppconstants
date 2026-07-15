"""Physical constants — ppconstants._physical

Scalar physical constants as module-level typed POST Python constants.

Reference source
----------------
Values follow the 2019 SI redefinition (BIPM, 9th SI brochure): constants
that are exact by definition are written with their exact decimal value.
Measured (CODATA) constants will cite CODATA 2022 as they land.

Currently seeded with the speed of light; the full scipy.constants scalar
table lands with ROADMAP Target 1.
"""

from postyp import f64

# Exact by SI definition (2019 redefinition).
c: f64 = 299792458.0
speed_of_light = c
