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
| Conversion kernels | `_conversions` | `lambda2nu`, `nu2lambda` |

Every constant is annotated exact / derived / measured with its reference
source (BIPM 9th SI brochure, CODATA 2022). The test suite checks values
against hardcoded references and physical consistency relations without
scipy, plus an exact-equality sweep against `scipy.constants` when scipy
is installed.

The full scipy.constants surface (mathematical constants, the CODATA
scalar table, SI prefixes, the unit catalog, `convert_temperature`, and
the `physical_constants` lookup API) is tracked target-by-target in
[`ROADMAP.md`](ROADMAP.md), including the pieces blocked on named
compiler capabilities.

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
from ppconstants import c, lambda2nu, nu2lambda

c                     # 299792458.0 (exact, SI definition)
lambda2nu(532e-9)     # 563519657894736.8 Hz

import numpy as np
nu2lambda(np.array([1.42040575e9, 4.74e14]))   # broadcasts elementwise
```

When the optional `ppconstants_native` extension is importable, the
package prefers its compiled ufuncs at import time
(`ppconstants.__native_available__`). Constants always come from the
Python source — they are compile-time values folded into kernels; getting
them exported into the C ABI (header + manifest) is upstream work tracked
in ROADMAP Target 6.

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
