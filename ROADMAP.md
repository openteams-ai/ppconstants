# ppconstants Roadmap

This roadmap is the coordination document for building `ppconstants` as a
complete POST Python implementation of `scipy.constants`, following the
[PostSciPy roadmap](https://github.com/openteams-ai/postpython/blob/main/postscipy-roadmap.md)
and the [ppspecial](https://github.com/openteams-ai/ppspecial) exemplar
layout.

The package's assigned compiler pressure: **module-level constants at
scale; cross-module constant imports.** Compiler and specification gaps
discovered here are reported as
[postpython issues](https://github.com/openteams-ai/postpython/issues)
with minimal reproducers — the filing is part of the work.

## Working Rules

- Keep `ppconstants` source free of compiler-specific escape hatches;
  every kernel runs interpreted and compiled.
- Verify compiler claims against a postpython checkout on `main`; record
  the commit hash with each verified milestone.
- `scipy` is the reference, never a runtime dependency. Prefer
  deterministic hardcoded reference values (exact SI definitions,
  CODATA 2022) so the suite runs without scipy.
- Each target lands as a small reviewable PR with tests in both execution
  modes and a status update in this file.

## Status Legend

- `Done`: implemented and verified.
- `Active`: currently being worked on.
- `Ready`: scoped and ready to pick up.
- `Blocked`: waiting on postpython compiler/spec work or an external decision.
- `Later`: intentionally deferred.

## Target 0: Baseline Package Health

Status: `Done` (verified against postpython `13bcf30`; kept under CI)

Acceptance criteria:

- Interpreted tests pass: `pixi run test` (or `python -m pytest tests/`).
- Native build passes with a postpython checkout on `main`:
  `pixi run build-native`.
- Extension build passes: `pixi run build-ext`.
- `scripts/build_native.py` reports every module and the full package
  shared library building.

Current notes:

- Scaffold seeded with `_physical` (`c`/`speed_of_light`) and
  `_conversions` (`lambda2nu`, `nu2lambda`), proving the pipeline this
  package exists to pressure: module-level constants, a constant alias,
  and a cross-module constant import folding into compiled kernels.
- Verified against postpython `13bcf30` (main): 19/19 tests pass
  (interpreted + C ABI via ctypes + ufunc extension), `build-native` and
  `build-ext` both succeed.
- Targets 1 through 4 verified against the same postpython commit: 252
  tests pass, including an exact-equality sweep against scipy 1.18.0 for
  every shared constant, all 16 temperature-scale pairs, and both
  wavelength/frequency kernels. All five modules and the package shared
  library compile; the extension registers three ufuncs.

## Target 1: Mathematical and Physical Scalar Constants

Status: `Done` (verified against postpython `13bcf30`)

The scipy.constants scalar table as module-level typed constants:

- Mathematical (`_mathematical`): `pi` (folded from the compile-time
  `postpyc.math.PI` import), `golden` / `golden_ratio` (folded constant
  expression).
- Exact SI, 2019 redefinition (`_physical`): `c` / `speed_of_light`,
  `h` / `Planck`, `e` / `elementary_charge`, `k` / `Boltzmann`,
  `N_A` / `Avogadro`.
- Exact by convention (`_physical`): `g` (standard gravity, CGPM 1901).
- Derived exact (`_physical`): `hbar` and `R` / `gas_constant` as folded
  constant expressions; `sigma` / `Stefan_Boltzmann` and `Wien`
  precomputed (closed forms need non-foldable operations), validated
  against their defining formulas in tests.
- Measured, CODATA 2022 (`_physical`): `mu_0`, `epsilon_0`,
  `G` / `gravitational_constant`, `alpha` / `fine_structure`, `Rydberg`,
  `m_e` / `electron_mass`, `m_p` / `proton_mass`, `m_n` / `neutron_mass`,
  `m_u` / `u` / `atomic_mass`.

Delivered: every constant documented as exact/derived/measured with its
reference source; aliases match scipy exactly; values checked against
hardcoded references and physical consistency relations unconditionally,
plus an exact-equality sweep against scipy 1.18.0 when installed; all
modules and the package shared library compile. Energy/unit-style values
(`eV`, `calorie`, ...) belong to Target 4.

## Target 2: SI Decimal and Binary Prefixes

Status: `Done` (verified against postpython `13bcf30`)

- Decimal: `quetta` ... `quecto` (all 24).
- Binary: `kibi` ... `yobi` (all 8).

Intentional divergence (documented in `_prefixes`): binary prefixes are
Float64, not Python int as in scipy — POST constants are fixed-width and
`zebi`/`yobi` exceed Int64; powers of two are exact in float64, so values
are numerically identical.

## Target 3: Conversion Kernels

Status: `Done` (verified against postpython `13bcf30`)

- `lambda2nu`, `nu2lambda`: exact relations through the SI-defined `c`,
  imported cross-module from `_physical`.
- `convert_temperature_code(val, old_code, new_code)`: compiled
  `@vectorize` kernel converting between Celsius, Kelvin, Fahrenheit, and
  Rankine through kelvin, matching scipy's arithmetic step for step.
  Scales are the public integer constants `CELSIUS`, `KELVIN`,
  `FAHRENHEIT`, `RANKINE`.
- `convert_temperature(val, old_scale, new_scale)`: scipy-compatible
  string API, an interpreted wrapper in the package manifest (spec §9.1
  CPython-boundary code) that maps scale names to codes and raises
  `NotImplementedError` for unsupported names, as scipy does.

**The design question is now settled by evidence, not preference.** Option 1
(a `Str`-parameterized kernel) was tried first, as the roadmap asked. It
type-checks, compiles, and is correct interpreted — but the compiled
kernel silently returns wrong answers, because the backend lowers the
string literal to `int64_t 0` and emits a pointer-vs-integer comparison.
Written up in
[`docs/upstream/01-str-comparison-miscompiles.md`](docs/upstream/01-str-comparison-miscompiles.md);
this is the highest-severity finding from this package so far, since it is
a silent wrong answer rather than a build failure.

Intentional divergence: the compiled C ABI offers the integer-code kernel,
not scipy's string signature. The Python API matches scipy exactly.

Known limitation: the kernel cannot signal a domain error for an
unrecognised code (returning `NAN` fails to lower,
[postpython#36](https://github.com/openteams-ai/postpython/issues/36)), so
validation lives in the wrapper and C consumers must pass valid codes. The
kernel treats an unknown code as "already kelvin".

## Target 4: Unit Conversion Constants Catalog

Status: `Done` (verified against postpython `13bcf30`)

87 constants in `_units`, covering every family in the scipy catalog:
mass, angle, time, length, pressure, area, volume, speed, temperature,
energy, power, and force.

Written as **folded constant expressions over their defining relations**
(`lb = 7000.0 * grain`, `mile = 1760.0 * yard`, `parsec = au / arcsec`,
`hp = 550.0 * foot * pound * g`) rather than precomputed decimals. Two
reasons: the derivation chain stays visible in the source, and it is the
only way to be bit-exact with scipy — `7000 * grain` is
`0.45359236999999997`, not the `0.45359237` the pound is defined as, and a
literal would silently disagree in the last bits.

This is the "constants at scale" pressure the package was assigned:
155 module-level constants, chained folded expressions up to four levels
deep, alias-of-alias references, and cross-module constant imports of
`pi`, `c`, `e`, and `g`. The compiler handled all of it with no new
issues — a positive result worth reporting upstream alongside the gaps.

## Target 5: CODATA `physical_constants` Table

Status: `Blocked` (compiler: Str-keyed containers)

`physical_constants` dict mapping name → (value, unit, uncertainty), plus
`value()`, `unit()`, `precision()`, `find()`, and `ConstantWarning`.

Reproducer confirmed and written up in
[`docs/upstream/03-str-keyed-containers.md`](docs/upstream/03-str-keyed-containers.md):
`postyp` exports no mapping type, and subscripting a module-level
container fails with `PP900 subscripted name TABLE is not a lowered local
array`. The draft also notes that `post-py check` passes on a module the
compiler then rejects.

`find()` additionally needs working string comparison in lowered code,
which Target 3 proved is broken — so this target depends on both drafts.

## Target 6: Constants in the Native C ABI

Status: `Blocked` (upstream postpython work)

Module-level constants fold into kernels but do **not** appear in the
compiled artifact's C ABI — no `pp_*` symbol, no header declaration, no
export-manifest entry (`collect_exports` resolves every export through
`resolve_function`, so constants are dropped). For a package that is
mostly constants, the shared library currently publishes only the three
conversion kernels.

Reproducer confirmed and written up in
[`docs/upstream/02-constants-missing-from-c-abi.md`](docs/upstream/02-constants-missing-from-c-abi.md),
which also notes that spec §9.1 ("Public symbols are top-level functions,
dataclasses, type aliases, and constants") and §9.1.1 (Package ABI over
exports) disagree on this point.

Pinned by `tests/test_native_abi.py::test_constants_absent_from_c_abi`:
that test asserts today's absent behavior, so it will fail when the
feature lands, which is the signal to adopt it.

## Target 7: Packaging, CI, and Release Flow

Status: `Active`

Done: `.github/workflows/ci.yml` with three jobs — interpreted tests on
Python 3.10 and 3.12, a native-build job compiling every module plus the
ufunc extension, and an optional scipy-comparison job marked
`continue-on-error` (a mismatch may mean scipy changed a reference value,
which should not block a merge).

All jobs install postpython from `main` per the working rules, rather than
a pinned release, so CI failures distinguish library regressions from
compiler drift.

Remaining: source-only PyPI releases (`py3-none-any`, no binary wheels, no
install/import-time compilation), the `libppconstants` + `ppconstants`
split prefix layout via `pixi run build-prefix`, and versioned release
notes separating the Python API, the C ABI, and the extension ABI.

## postpython Request Backlog

Needs discovered from ppconstants. Each is written up with a confirmed
minimal reproducer under [`docs/upstream/`](docs/upstream/), ready to file.

Ordered by severity:

1. **`Str` comparison silently miscompiles**
   ([draft](docs/upstream/01-str-comparison-miscompiles.md)) — a string
   literal lowers to `int64_t 0` and the comparison becomes
   pointer-vs-integer, so valid POST Python that is correct interpreted
   returns wrong answers compiled, with no diagnostic. The primary ask is
   to **diagnose instead of miscompile**; full `Str` support is secondary.
2. **Constants absent from the C ABI / export manifest**
   ([draft](docs/upstream/02-constants-missing-from-c-abi.md), Target 6) —
   blocks the native-library story for constant-heavy packages, and the
   spec is self-inconsistent on whether constants are exports.
3. **Str-keyed containers**
   ([draft](docs/upstream/03-str-keyed-containers.md), Target 5) — blocks
   `physical_constants` and its four accessor functions. Also records that
   `post-py check` passes on a module the compiler rejects.

Positive result worth reporting alongside the gaps: module-level constant
folding (#11) held up at this package's full scale — 155 constants,
four-deep folded expression chains, alias-of-alias references, and
cross-module constant imports, with no new issues.

Watching: [postpython#36](https://github.com/openteams-ai/postpython/issues/36)
(NAN/INF fail to lower) — the reason `convert_temperature_code` cannot
signal a domain error in the kernel.

## Publication Checklist for Each Milestone

Before marking a target `Done`, publish:

- source changes and tests,
- interpreted test output and native build output,
- the postpython commit hash used for verification,
- any postpython issue/request generated by the work,
- README and roadmap status updates.
