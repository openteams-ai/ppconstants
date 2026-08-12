# Str comparison silently miscompiles: string literal lowered to `int64_t 0`

**Severity: high — silent wrong answer, no diagnostic.**
Status: draft, ready to file at openteams-ai/postpython.

## Summary

A `Str` parameter compared against a string literal is accepted by the
checker, compiles without a warning, and produces the *correct* result in
interpreted mode — but the compiled kernel always takes the false branch.

The backend lowers the string literal `"C"` to `int64_t 0` and emits a
pointer-vs-integer comparison, so `scale == "C"` is really
`scale == NULL`, which is false for every non-null argument.

Found while implementing `ppconstants._conversions` (Target 3,
`convert_temperature`), where scipy's API spells the temperature scales as
strings.

## Minimal reproducer

```python
# str_probe.py
from postyp import f64, Str
from postpyc import vectorize


@vectorize
def scale_offset(val: f64, scale: Str) -> f64:
    if scale == "C":
        return val + 273.15
    return val
```

```python
from pathlib import Path
from postpyc.build import build_file

build_file(Path("str_probe.py"), output=Path("p.so"), emit_header=True)
```

## Observed

`post-py check str_probe.py` passes. The build succeeds. The header is
generated correctly:

```c
double pp_scale_offset(double val, const char* scale);
```

Interpreted mode is correct:

```python
>>> import str_probe
>>> str_probe.scale_offset(0.0, "C")
273.15
```

Compiled, through the stable C ABI, is wrong:

```python
>>> import ctypes
>>> d = ctypes.CDLL("./p.so")
>>> f = d.pp_scale_offset
>>> f.restype = ctypes.c_double
>>> f.argtypes = [ctypes.c_double, ctypes.c_char_p]
>>> f(0.0, b"C")
0.0        # expected 273.15
```

## Cause

The emitted C for the comparison:

```c
double scale_offset(double _val, const char* _scale)
{
    entry:;
        int64_t _c1 = 0;              /* <-- the literal "C" */
        bool _cmp2 = _scale == _c1;   /* <-- pointer vs integer */
        if (_cmp2) goto if_then3; else goto if_after4;
    if_then3:;
        double _f5 = 273.15;
        double _v6 = _val + _f5;
        return _v6;
    if_after4:;
        return _val;
}
```

Two separate problems:

1. **String literals are not lowered.** `"C"` becomes `int64_t 0` rather
   than a string constant.
2. **`Str` equality is lowered as scalar `==`** rather than a content
   comparison (`strcmp`), so even with a correct literal it would compare
   pointers, not text.

C compilers accept `pointer == 0` as a null check, so nothing warns.

There is also a ufunc-layer concern: the generated loop reads the argument
as `*((const char* *)(arg1 + i * step1))`, i.e. it expects an array of
`char*`. NumPy has no dtype that produces that layout, so a `Str`
parameter is not reachable through the registered ufunc either.

## Suggested resolution

Any of these would unblock library code; the first is the important one:

- **Diagnose rather than miscompile.** If `Str` values, string literals,
  or `Str` comparisons are not supported in lowered code yet, emit a
  compiler error (a `PP` diagnostic) instead of silently emitting a
  pointer-vs-integer comparison. A build failure is recoverable; a wrong
  number in a physical-constants library is not.
- Then, if `Str` is meant to be usable in POST Core kernels: lower string
  literals to C string constants and lower `Str` `==`/`!=` to a content
  comparison. Spec §4.1 lists `Str` as a scalar dtype with no stated
  restriction, so today's behavior contradicts the spec.
- Alternatively, state in the spec that `Str` is a CPython-boundary type
  only, not usable in `@vectorize`/`@guvectorize` kernels, and have the
  checker reject it there.

## Workaround in use

`ppconstants` takes integer scale codes in the compiled kernel
(`convert_temperature_code(val, old_code, new_code)`) and keeps the
scipy-compatible string API as an interpreted wrapper in the package
manifest. This works, but it means the compiled C ABI cannot offer the
scipy signature.
