# Accuracy and reference sources

Accuracy is a deliverable, not an afterthought (PostSciPy working rule 6).
This page states, for every part of the public API, where the numbers come
from, what tolerance is claimed, and the largest error actually observed.

All figures below were measured against **scipy 1.18.0** with the package
compiled by **postpython `main` @ `13bcf30`**, and are reproduced by the
test suite on every run.

## Summary

| Surface | Reference | Claimed tolerance | Max observed error |
|---|---|---|---|
| 155 scalar constants | scipy 1.18.0 / CODATA 2022 / BIPM | bit-exact | 0 (all 155 exact) |
| `physical_constants` (445 entries) | scipy 1.18.0 | bit-exact | 0 |
| `lambda2nu`, `nu2lambda` | scipy 1.18.0 | bit-exact | 0.0 relative |
| `convert_temperature` | scipy 1.18.0 | bit-exact | 0.0 absolute |
| Compiled vs interpreted, all kernels | interpreted mode | bit-exact | 0.0 |

"Bit-exact" is a real claim here, not a rounded one: the tests use `==`,
not a tolerance, and the measured error is exactly zero.

## Why the constants are bit-exact and not merely close

Physical constants are published decimals, so agreement should be exact.
The one place this is easy to get wrong is **derived** units, where the
defining relation and the published decimal are not the same float64.

The avoirdupois pound is defined as 0.45359237 kg. Computed the way it is
actually derived, `7000 * grain`, float64 gives `0.45359236999999997`.
Those differ in the last bits. scipy computes it, so `ppconstants` writes
the derivation chain rather than the decimal:

```python
grain: f64 = 64.79891e-6
lb: f64 = 7000.0 * grain        # not 0.45359237
```

The compiler folds this at build time, so there is no runtime cost, the
source documents its own provenance, and the value matches scipy exactly.
The same applies to `mile`, `parsec`, `psi`, `hp`, `Btu`, and the rest of
the catalog.

## Reference sources by group

### Mathematical constants (`_mathematical`)

| Constant | Source |
|---|---|
| `pi` | `postpyc.math.PI`, folded at compile time |
| `golden`, `golden_ratio` | `(1 + sqrt(5)) / 2`, folded constant expression |

Validated additionally by the defining property `golden**2 == golden + 1`
to within 1e-15.

### Physical constants (`_physical`)

| Group | Source | Exactness |
|---|---|---|
| `c`, `h`, `e`, `k`, `N_A` | BIPM 9th SI brochure, 2019 redefinition | exact by definition |
| `g` | CGPM 1901 | exact by convention |
| `hbar`, `R` | folded expressions over exact values | exact |
| `sigma`, `Wien` | precomputed; closed forms need non-foldable ops | exact to float64 |
| `mu_0`, `epsilon_0`, `G`, `alpha`, `Rydberg`, `m_e`, `m_p`, `m_n`, `m_u` | CODATA 2022 | measured |

Beyond value comparison, the suite checks physical relations that hold
independently of the reference:

| Relation | Tolerance | Purpose |
|---|---|---|
| `hbar == h / (2 pi)` | exact | derived-constant consistency |
| `R == N_A * k` | exact | derived-constant consistency |
| `sigma` vs `2 pi^5 k^4 / (15 h^3 c^2)` | 1e-14 relative | closed form of a precomputed value |
| `Wien` vs `(h c / k) / 4.965114231744276` | 1e-14 relative | closed form of a precomputed value |
| `alpha` vs `e^2 / (4 pi epsilon_0 hbar c)` | 1e-9 relative | cross-check of measured values |
| `mu_0 * epsilon_0 * c^2 == 1` | 1e-9 absolute | cross-check of measured values |

The 1e-9 tolerances are set by the experimental uncertainty of the
measured inputs, not by floating-point error.

### Prefixes (`_prefixes`)

Exact powers of ten and two. Decimal reciprocal pairs (`kilo * milli`)
are checked to 1e-9, which is the float64 limit for values like
`1e30 * 1e-30`; the binary ladder is checked exactly.

### Unit catalog (`_units`)

Derivation chains follow scipy, which follows NIST SP 811 and the 1959
international yard-and-pound agreement. Each family is additionally
checked against its defining relation (for example `psi == pound * g /
inch^2`, `parsec == au / arcsec`) rather than only against scipy, so the
suite still means something without scipy installed.

### CODATA table (`_codata`)

Transcribed from scipy 1.18.0: 355 current CODATA 2022 entries plus 90
superseded entries retained from the 2002-2018 adjustments. Values,
units, and uncertainties all compared exactly; `find()` and the
`ConstantWarning` behaviour are compared against scipy for every current
key.

**Known upstream anomaly.** Two keys, `natural unit of momentum` and
`natural unit of momentum in MeV/c`, carry their CODATA 2018 value and
uncertainty in scipy's published `physical_constants` even though scipy's
own current-CODATA table holds the 2022 figures. `ppconstants` reproduces
scipy's published values so the table stays a drop-in replacement, and
pins this in
`tests/test_codata.py::test_scipy_stale_value_anomaly_is_reproduced`. If
scipy fixes it, that test fails and the table should be re-synced.

## Intentional divergences from scipy

These are deliberate and tested, not accidents.

| Divergence | Reason |
|---|---|
| Binary prefixes (`kibi` … `yobi`) are `float64`, not Python `int` | POST constants are fixed-width and `zebi`/`yobi` exceed `Int64`. Every power of two is exact in float64, so values compare equal to scipy's ints. |
| The compiled C ABI exposes `convert_temperature_code(val, old_code, new_code)` rather than scipy's string signature | The compiler miscompiles `Str` comparison (see `docs/upstream/01`). The **Python** API matches scipy exactly. |
| `_codata` is interpreted-only, outside the compiled artifact | POST Python has no `Str`-keyed container (see `docs/upstream/03`). |
| Constants are absent from the generated C header and export manifest | Compiler gap (see `docs/upstream/02`), pinned by a regression test. |

## Edge cases covered

- `convert_temperature`: absolute zero in all four scales, the -40 °C =
  -40 °F crossover, water's freezing and boiling points, all 16 scale
  pairs round-tripped, and unsupported scale names raising
  `NotImplementedError` as scipy does.
- `lambda2nu` / `nu2lambda`: round-tripped across 27 decades
  (1e-12 to 1e15), plus the 21 cm hydrogen line and common laser lines.
- `physical_constants`: every entry checked for shape, type, and
  non-negative uncertainty; exact constants confirmed to have precision 0.

## Reproducing these numbers

```bash
pixi run -e dev test                     # everything, including the scipy sweep
python -m pytest tests/test_scipy_compat.py -v   # the comparison sweep alone
```

The scipy sweep is skipped automatically when scipy is not installed, so
the suite runs without it. In CI the sweep is a separate,
`continue-on-error` job: a mismatch may mean scipy changed a reference
value, which should be investigated rather than treated as a build break.
