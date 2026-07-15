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

Status: `Active`

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

## Target 1: Mathematical and Physical Scalar Constants

Status: `Ready` (seeded: `c`, `speed_of_light`)

The scipy.constants scalar table as module-level typed constants:

- Mathematical: `pi`, `golden`, `golden_ratio`.
- Exact SI (2019 redefinition): `c`, `h`, `e` (`elementary_charge`), `k`
  (`Boltzmann`), `N_A` (`Avogadro`), plus derived exact values
  (`hbar`, `R` / `gas_constant`, `sigma` / `Stefan_Boltzmann`, `zero_Celsius`).
- Measured (CODATA 2022): `G` (`gravitational_constant`), `g`, `alpha`
  (`fine_structure`), `mu_0`, `epsilon_0`, `Wien`, `Rydberg`, `m_e`
  (`electron_mass`), `m_p` (`proton_mass`), `m_n` (`neutron_mass`),
  `m_u` (`atomic_mass`), `eV`, `calorie`, ...

Acceptance criteria:

- Every constant documented with its reference source (SI brochure or
  CODATA 2022) and whether it is exact or measured.
- Aliases match scipy's names exactly.
- Values verified against scipy in an optional scipy-gated test, and
  against hardcoded references unconditionally.
- Full set compiles: constants fold into kernels; the package shared
  library builds.

## Target 2: SI Decimal and Binary Prefixes

Status: `Ready`

- Decimal: `quetta` ... `quecto` (scipy: `yotta` ... `quecto` plus
  `quetta`/`ronna` since CODATA 2022 era; match current scipy `main`).
- Binary: `kibi` ... `yobi`.

Same acceptance criteria as Target 1.

## Target 3: Conversion Kernels

Status: `Active` (`lambda2nu`, `nu2lambda` done in scaffold)

Remaining: `convert_temperature(val, old_scale, new_scale)`.

Open design question: scipy's signature takes string scale names. POST
`@vectorize` kernels take scalar dtypes — `Str` parameters in a ufunc are
untested territory. Options, in preference order:

1. `Str`-parameterized kernel if the compiler supports it (exercise, then
   file gaps upstream).
2. Scale-pair kernels (`_celsius_to_kelvin`, ...) behind a thin
   CPython-boundary dispatcher in `__init__.py`, documented as an
   intentional divergence of the compiled ABI (not the Python API).

Acceptance criteria:

- scipy-compatible Python API (`convert_temperature(x, "Celsius", "Kelvin")`).
- Reference values hardcoded (0 °C = 273.15 K, absolute zero, boiling
  point across all four scales); optional scipy comparison.
- Whatever cannot be expressed in pure POST Python is filed upstream with
  a reproducer and referenced here.

## Target 4: Unit Conversion Constants Catalog

Status: `Ready`

The scipy.constants unit catalog as typed constants, family by family:
mass (`gram`, `metric_ton`, `pound`, `ounce`, ...), angle (`degree`,
`arcmin`, `arcsec`), time (`minute` ... `Julian_year`), length (`inch`,
`mile`, `light_year`, `parsec`, ...), pressure (`atm`, `bar`, `torr`,
`psi`), area, volume, speed, energy (`eV`, `calorie`, `erg`, ...), power
(`hp`), force (`dyn`, `lbf`, `kgf`), temperature (`degree_Fahrenheit`).

This is "constants at scale" — expect it to stress compile-time constant
folding performance and namespace/manifest size; report findings upstream.

## Target 5: CODATA `physical_constants` Table

Status: `Blocked` (compiler: Str-keyed containers)

`physical_constants` dict mapping name → (value, unit, uncertainty), plus
`value()`, `unit()`, `precision()`, `find()`, and `ConstantWarning`.

First action when starting: file a postpython issue with a minimal
reproducer for `Str`-keyed container support (per the package README and
the PostSciPy working rules), and link it here.

## Target 6: Constants in the Native C ABI

Status: `Blocked` (upstream postpython work; issue to be filed)

Discovered at scaffold time: module-level constants fold into kernels but
do **not** appear in the compiled artifact's C ABI — no `pp_*` symbol, no
header `#define`/`extern const double`, no export-manifest entry
(`collect_exports` in postpyc only exports functions). For a package that
is mostly constants, the plain shared-library target currently carries
only the conversion kernels.

Action: file a postpython issue proposing constant exports in Package ABI
v1 (header declarations + manifest entries), with this package as the
motivating consumer and a minimal reproducer. Link it here once filed.

## Target 7: Packaging, CI, and Release Flow

Status: `Later`

Mirrors ppspecial Target 11: CI for interpreted tests and native builds
against postpython `main`, optional scipy-comparison job, source-only
PyPI releases (`py3-none-any`, no binary wheels, no install/import-time
compilation), and the `libppconstants` + `ppconstants` split prefix
layout via `pixi run build-prefix`.

## postpython Request Backlog

Needs discovered from ppconstants; items become postpython issues when
actively worked.

- **Constants in the C ABI / export manifest** (Target 6) — to file.
- **Str-keyed containers** for the CODATA table (Target 5) — to file when
  Target 5 starts.
- **Str scalar parameters in `@vectorize` kernels** (Target 3) — exercise
  first, file if it fails.
- Watching: [postpython#36](https://github.com/openteams-ai/postpython/issues/36)
  (NAN/INF fail to lower) — relevant to scipy-compatible NaN behavior in
  `convert_temperature` domain handling.

## Publication Checklist for Each Milestone

Before marking a target `Done`, publish:

- source changes and tests,
- interpreted test output and native build output,
- the postpython commit hash used for verification,
- any postpython issue/request generated by the work,
- README and roadmap status updates.
