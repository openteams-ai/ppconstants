# ppconstants

Physical and mathematical constants, in POST Python.

`ppconstants` reimplements `scipy.constants` in
[POST Python](https://github.com/openteams-ai/postpython) — every constant
is a module-level typed constant and every conversion function is a
fully-typed `@vectorize` kernel that runs under the standard CPython
interpreter **and** compiles ahead-of-time to native code (a plain C
shared library and a NumPy ufunc extension module) with the POST Python
reference compiler (`postpyc`).

Status: **Active** — scaffolded and seeded. It is part of the
[PostSciPy effort](https://github.com/openteams-ai/postpython/blob/main/postscipy-roadmap.md)
to rebuild SciPy one subpackage at a time as the compiler's proving ground.
Primary compiler pressure this package generates: module-level constants
at scale; cross-module constant imports.

## What this looks like

```python
from postyp import f64
from postpyc import vectorize
from ppconstants._physical import c   # cross-module constant import


@vectorize
def lambda2nu(lambda_: f64) -> f64:
    """Convert wavelength in metres to optical frequency in Hz."""
    return c / lambda_
```

Under CPython this is immediately callable (scalars, or NumPy arrays with
broadcasting when NumPy is installed). The `postpyc` compiler folds the
constant and lowers the kernel to a C99 NumPy-ufunc loop in a native
shared library.

## Implemented

| Family | Module | Names |
|---|---|---|
| Mathematical constants | `_mathematical` | `pi`, `golden` / `golden_ratio` |
| Physical constants (exact SI) | `_physical` | `c` / `speed_of_light`, `h` / `Planck`, `e` / `elementary_charge`, `k` / `Boltzmann`, `N_A` / `Avogadro`, `g` |
| Physical constants (derived) | `_physical` | `hbar`, `R` / `gas_constant`, `sigma` / `Stefan_Boltzmann`, `Wien` |
| Physical constants (CODATA 2022) | `_physical` | `mu_0`, `epsilon_0`, `G` / `gravitational_constant`, `alpha` / `fine_structure`, `Rydberg`, `m_e` / `electron_mass`, `m_p` / `proton_mass`, `m_n` / `neutron_mass`, `m_u` / `u` / `atomic_mass` |
| SI decimal prefixes | `_prefixes` | `quetta` ... `quecto` (all 24) |
| Binary prefixes | `_prefixes` | `kibi` ... `yobi` (float64; intentional divergence from scipy's int) |
| Unit catalog | `_units` | 87 constants: mass, angle, time, length, pressure, area, volume, speed, temperature, energy, power, force |
| Conversion kernels | `_conversions` | `lambda2nu`, `nu2lambda`, `convert_temperature` |

That is 155 public constants and 3 compiled kernels — the whole
`scipy.constants` surface except the CODATA `physical_constants` lookup
table, which is blocked upstream (see below).

Every constant is annotated exact / derived / measured with its reference
source (BIPM 9th SI brochure, CODATA 2022, NIST SP 811). Unit constants
are written as folded expressions over their defining relations
(`lb = 7000.0 * grain`, `parsec = au / arcsec`) rather than precomputed
decimals, so the derivation stays visible and the values are bit-exact
with scipy. The test suite checks values against hardcoded references and
physical consistency relations without scipy, plus an exact-equality sweep
against `scipy.constants` when scipy is installed.

Progress is tracked target-by-target in [`ROADMAP.md`](ROADMAP.md).

## Installation and development

`ppconstants` follows the postpython distribution policy: pure-source
artifacts only, no binary wheels, no install- or import-time compilation.

```bash
git clone https://github.com/openteams-ai/ppconstants.git
cd ppconstants
python -m pip install -e ".[dev]"
```

Or with [pixi](https://pixi.sh/) (also installs a C compiler for native
builds):

```bash
pixi install -e dev
pixi run -e dev test            # test suite: interpreted + compiled modes
pixi run -e dev build-native    # plain C shared library + header + manifest
pixi run -e dev build-ext       # ppconstants_native, a NumPy-ufunc extension
pixi run -e dev build-prefix    # libppconstants prefix layout under dist/prefix
```

## Usage

```python
from ppconstants import c, mile, lambda2nu, convert_temperature

c                                              # 299792458.0 (exact, SI definition)
mile                                           # 1609.3439999999998 metres
lambda2nu(532e-9)                              # 563519657894736.8 Hz
convert_temperature(100.0, "Celsius", "F")     # 212.0

import numpy as np
convert_temperature(np.array([-40.0, 0.0, 37.0]), "C", "F")   # broadcasts
```

When the optional `ppconstants_native` extension is importable, the
package prefers its compiled ufuncs at import time
(`ppconstants.__native_available__`). Constants always come from the
Python source — they are compile-time values folded into kernels; getting
them exported into the C ABI (header + manifest) is upstream work tracked
in ROADMAP Target 6.

## Compiler findings

Driving the compiler is half the point of this package (see the
[PostSciPy roadmap](https://github.com/openteams-ai/postpython/blob/main/postscipy-roadmap.md)).
Findings so far are written up with confirmed minimal reproducers in
[`docs/upstream/`](docs/upstream/):

1. [`Str` comparison silently miscompiles](docs/upstream/01-str-comparison-miscompiles.md)
   — a string literal lowers to `int64_t 0`, so `scale == "C"` is always
   false in compiled code while interpreted mode is correct. This is why
   `convert_temperature`'s compiled kernel takes integer scale codes.
2. [Constants are absent from the C ABI](docs/upstream/02-constants-missing-from-c-abi.md)
   — they fold into kernels but get no `pp_*` symbol, header declaration,
   or manifest entry.
3. [Str-keyed containers are unavailable](docs/upstream/03-str-keyed-containers.md)
   — blocks the CODATA `physical_constants` table and its accessors.

On the positive side, module-level constant folding held up at this
package's full scale: 155 constants, folded expression chains four levels
deep, alias-of-alias references, and cross-module constant imports, with
no new compiler issues.

## Working rules (summary)

- Pure POST Python: no compiler-specific escape hatches; every kernel
  runs interpreted and compiled.
- `scipy` is the reference, never a runtime dependency. Tests prefer
  deterministic hardcoded reference values (SI definitions, CODATA 2022).
- Compiler gaps go upstream as
  [postpython issues](https://github.com/openteams-ai/postpython/issues)
  with minimal reproducers, not silent workarounds.
- Verify against a postpython checkout on `main`; record the commit hash
  with each verified milestone.

The full rules and the definition of done live in the
[PostSciPy roadmap](https://github.com/openteams-ai/postpython/blob/main/postscipy-roadmap.md).
