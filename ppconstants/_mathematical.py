"""Mathematical constants — ppconstants._mathematical

Module-level typed POST Python constants. `pi` folds from the
compile-time `postpyc.math.PI` import; `golden` folds from a literal
constant expression, matching scipy's (1 + sqrt(5)) / 2.
"""

from postyp import f64
from postpyc.math import PI

pi: f64 = PI
golden: f64 = (1.0 + 5.0 ** 0.5) / 2.0
golden_ratio = golden
