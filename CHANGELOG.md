# Changelog

All notable changes to `ppconstants` are recorded here.

Three interfaces are versioned separately and are called out per entry:

- **Python API** — what `import ppconstants` gives you.
- **Native C ABI** — the `pp_*` exports in `libppconstants.so`, described
  by `ppconstants.h` and `ppconstants.json`.
- **Extension ABI** — the ufuncs in `ppconstants_native`.

## [Unreleased]

### Python API

- Added the full `scipy.constants` scalar surface: 155 public constants
  across mathematical (`pi`, `golden`), physical (exact SI, conventional,
  derived, and CODATA 2022 measured), SI decimal and binary prefixes, and
  the 87-constant unit catalog. All scipy aliases included.
- Added `lambda2nu`, `nu2lambda`, and `convert_temperature` with scipy's
  string scale names.
- Added the CODATA lookup surface: `physical_constants` (445 entries),
  `value`, `unit`, `precision`, `find`, and `ConstantWarning`.
- Every shared name is bit-exact against scipy 1.18.0.

### Native C ABI

- `libppconstants.so` exports `pp_lambda2nu`, `pp_nu2lambda`, and
  `pp_convert_temperature_code`, with generated `ppconstants.h` and
  `ppconstants.json` sidecars.
- `pixi run build-prefix` produces the package-manager layout
  (`lib/`, `include/`, `share/postpyc/`).
- **Known limitation:** constants do not appear in the C ABI. They fold
  into kernels but get no `pp_*` symbol, header declaration, or manifest
  entry. Upstream gap, see `docs/upstream/02-constants-missing-from-c-abi.md`.

### Extension ABI

- `ppconstants_native` registers `lambda2nu`, `nu2lambda`, and
  `convert_temperature_code` as real `numpy.ufunc` objects. Importing
  `ppconstants` prefers them automatically when the extension is present.

### Divergences from scipy

- Binary prefixes are `float64` rather than Python `int` (`zebi`/`yobi`
  exceed `Int64`; values still compare equal).
- The compiled C ABI takes integer scale codes for temperature
  conversion; the Python API keeps scipy's string signature. Forced by a
  compiler bug, see `docs/upstream/01-str-comparison-miscompiles.md`.
- `ppconstants._codata` is interpreted-only CPython-boundary code rather
  than compiled POST Python, because POST Python has no `Str`-keyed
  container yet. See `docs/upstream/03-str-keyed-containers.md`.

### Upstream findings produced by this work

- `Str` comparison silently miscompiles: a string literal lowers to
  `int64_t 0`, so the comparison always fails in compiled code while
  interpreted mode is correct. High severity — a silent wrong answer.
- Module-level constants are absent from the package C ABI, and spec
  §9.1 and §9.1.1 disagree on whether they should be.
- No `Str`-keyed containers, blocking the CODATA table from being POST
  Python. The structural checker also accepts a module the compiler
  rejects.

### Verification

postpython `main` @ `13bcf30`: 296 tests pass across interpreted, C ABI,
and compiled-ufunc modes; 116 of those still pass with scipy uninstalled,
which is what CI blocks on. All five POST modules and the package shared
library compile; the extension registers three ufuncs. Kernels are
bit-identical between compiled and interpreted execution.

An independent review verified the value claims by byte-comparing all 155
constants and all 445 table entries against scipy, reproduced all three
upstream findings, and mutation-tested the suite (90 injected value
errors, 90 caught). It found no numerical defect. It did find that scipy
was undeclared in every environment, so the comparison sweep silently
skipped and five unit families were left without a scipy-independent
pin — fixed here, along with four documentation claims that overstated
how the numbers were asserted.
