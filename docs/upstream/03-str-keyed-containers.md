# Str-keyed containers for the CODATA lookup table

**Severity: medium — blocks a whole public API family.**
Status: draft, ready to file at openteams-ai/postpython.

## Summary

`scipy.constants` exposes `physical_constants`, a dict mapping a constant
name to `(value, unit, uncertainty)`, plus `value(name)`, `unit(name)`,
`precision(name)`, and `find(sub)` built on it. That is roughly 350
entries and four public functions, and it is the last unimplemented
family in `ppconstants`.

POST Python has no container keyed by `Str` today, and `postyp` exports no
mapping type at all, so this family cannot be expressed.

## Minimal reproducer

```python
# strdict.py
from postyp import f64, Str, Dict          # <-- Dict does not exist
from postpyc import vectorize

TABLE: Dict[Str, f64] = {"speed of light in vacuum": 299792458.0}


@vectorize
def value(name: Str) -> f64:
    return TABLE[name]
```

## Observed

`postyp` has no mapping type:

```text
ImportError: cannot import name 'Dict' from 'postyp'
```

With the annotation removed so the module parses, the checker passes but
the build fails:

```text
$ post-py check strdict.py     # rc 0, no diagnostics
$ python -c "from postpyc.build import build_file; from pathlib import Path; build_file(Path('strdict.py'), output=Path('sd.so'))"
postpyc.build.BuildError: Compiler errors building 'strdict.py':
  9:17: PP900 subscripted name `TABLE` is not a lowered local array
```

Worth noting on its own: the structural checker accepts a module the
compiler then rejects, so `post-py check` passing is not a reliable
predictor of a successful build.

## What this family actually needs

Listed smallest-first, since a partial answer still unblocks most of the
API:

1. **A read-only, compile-time-constant mapping from `Str` to a scalar**,
   with lookup by key. That alone delivers `value()`, `unit()`, and
   `precision()` if the value/unit/uncertainty triple is split across
   three tables.
2. **Tuple- or struct-valued entries**, so one table can hold
   `(value, unit, uncertainty)` per key. This overlaps with the
   struct/`@dataclass` work other packages want.
3. **Substring search over the key set** for `find()`. This needs string
   comparison to work in lowered code at all, which today it does not —
   see the companion draft on `Str` comparison miscompiling.

A frozen, perfect-hash-style lookup built at compile time would fit the
POST model well: the table is known statically, never mutated, and wants
no allocation.

## Interim plan for ppconstants

Hold Target 5. If this stays blocked, a fallback is to ship
`physical_constants` and the four accessors as a pure-Python,
interpreted-only module that is explicitly outside the compiled artifact
(spec §9.1 CPython-boundary code), and document the divergence. That keeps
the Python API scipy-compatible, but it means the flagship
"constants at scale" package cannot express its largest constant table in
POST Python, which seems like the wrong outcome for the language.
