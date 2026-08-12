# Module-level constants are absent from the package C ABI

**Severity: medium — blocks the native-library story for constant-heavy packages.**
Status: draft, ready to file at openteams-ai/postpython.
Related: [#11](https://github.com/openteams-ai/postpython/issues/11) (module-level
constants, delivered), [#12](https://github.com/openteams-ai/postpython/issues/12)
(package C ABI, delivered).

## Summary

Module-level constants fold correctly into compiled kernels (#11 works
well — `ppconstants` has 155 of them, including cross-module imports and
folded expression chains). But they do not appear in the compiled
artifact's interface: no `pp_*` symbol, no declaration in the generated
header, no entry in the export manifest.

Spec §9.1 says "Public symbols are top-level functions, dataclasses, type
aliases, **and constants** not prefixed with `_`", and §9.1.1 defines the
Package ABI over "exports". Constants satisfy the first sentence but are
not treated as exports, so the two sections disagree.

This matters most for a package whose entire purpose is constants. A C
consumer that links `libppconstants.so` can call `pp_lambda2nu`, but there
is no way to read `c`, `pi`, or `zero_Celsius` from the artifact — they
exist only as immediates baked into kernel bodies.

## Minimal reproducer

```python
# const_abi.py
from postyp import f64
from postpyc import vectorize

SPEED_OF_LIGHT: f64 = 299792458.0


@vectorize
def scale(x: f64) -> f64:
    return x * SPEED_OF_LIGHT
```

```python
from pathlib import Path
import json
from postpyc.build import build_file

build_file(Path("const_abi.py"), output=Path("ca.so"),
           emit_header=True, emit_manifest=True)

print("in header:", "SPEED_OF_LIGHT" in Path("ca.h").read_text())
print("exports:", [e["name"] for e in json.loads(Path("ca.json").read_text())["exports"]])
```

## Observed

```text
in header: False
exports: ['scale']
$ nm -D --defined-only ca.so | grep -c SPEED_OF_LIGHT
0
```

The constant folded into `scale` correctly (calling `pp_scale(1.0)`
returns `299792458.0`), so this is purely about the published interface.

`collect_exports` in `postpyc/compiler/backend/abi.py` walks
`entry.post_imports`, `entry.functions`, and module aliases, resolving
each through `resolve_function`; a name that resolves to a constant is
dropped.

## Suggested resolution

Extend Package ABI v1 with a constant export kind:

- **Header**: emit each public constant as a declaration a C consumer can
  use. Either a macro (`#define PP_SPEED_OF_LIGHT 299792458.0`) or an
  `extern const double pp_SPEED_OF_LIGHT;` backed by a real definition in
  the artifact. The `extern` form is more useful (it survives `dlopen`
  and is readable from ctypes/cffi); a macro is cheaper and keeps the
  artifact free of data symbols. Both would satisfy this package.
- **Manifest**: add entries with `"kind": "constant"`, carrying the Python
  name, dtype, and value. Downstream tools (bindings generators, package
  recipes) can then see them.
- **Symbol**: if the `extern` form is chosen, define `pp_<name>` as a
  read-only data symbol in the artifact.

Keeping the value in the manifest is the single most useful piece, since
it lets non-C consumers reproduce the constant table without parsing
Python.

## Regression pin in ppconstants

`tests/test_native_abi.py::test_constants_absent_from_c_abi` asserts the
current (absent) behavior for `c`, `pi`, `zero_Celsius`, and `kilo`. When
this lands upstream that test will fail, which is the intended signal to
adopt the feature and update the roadmap.
