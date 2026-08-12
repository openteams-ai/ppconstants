# Contributing to ppconstants

This guide should let you land one constant, or one kernel, without
reading the whole project first.

## Setup

```bash
git clone https://github.com/openteams-ai/ppconstants.git
cd ppconstants
pixi install -e dev
pixi run -e dev test
```

Or with pip, plus a postpython checkout for compiler work:

```bash
python -m pip install -e ".[dev]"
python -m pip install "postpyc @ git+https://github.com/openteams-ai/postpython.git"
```

Compiler results only count against postpython `main`
(PostSciPy working rule 3). Check before quoting a build result:

```bash
git -C /path/to/postpython rev-parse --abbrev-ref HEAD   # must be main
git -C /path/to/postpython rev-parse --short HEAD        # record this hash
```

## The four commands

| Command | What it proves |
|---|---|
| `pixi run -e dev test` | interpreted, C ABI, and compiled ufunc modes all agree |
| `pixi run -e dev build-native` | every module and the package compile to a C shared library |
| `pixi run -e dev build-ext` | the NumPy ufunc extension builds and imports |
| `pixi run -e dev build-prefix` | the `libppconstants` package-manager layout builds |

## Layout

```text
ppconstants/
  __init__.py       Python namespace manifest. Also imports _codata,
                    which is NOT POST Python, so the compiler must not
                    use this file as its entry.
  __post__.py       The compiler's entry point (spec §9.1). Re-exports
                    only the POST translation units.
  _mathematical.py  pi, golden
  _physical.py      exact SI, conventional, derived, CODATA 2022 scalars
  _prefixes.py      SI decimal and binary prefixes
  _units.py         the unit catalog (mass, length, energy, ...)
  _conversions.py   @vectorize kernels
  _codata.py        CODATA table + accessors — interpreted only
tests/              one file per module, plus native ABI / ext / scipy
docs/upstream/      compiler findings with minimal reproducers
```

**`__init__.py` versus `__post__.py` is the one structural subtlety.**
Build scripts and tests pass the package *directory* to the compiler, not
`__init__.py`, because `__post__.py` only takes precedence when the
compiler is handed a directory. If you add a module, add it to both files
(and to `EXPECTED_NATIVE` in `scripts/build_native.py`) — unless it is
CPython-boundary code, in which case it goes in `__init__.py` only.

## Adding a constant

1. Put it in the module for its family, with a `f64` annotation.
2. **Write the derivation, not the decimal**, when the value is derived:

   ```python
   yard: f64 = 3.0 * foot        # yes
   yard: f64 = 0.9144            # no — may differ from scipy in the last bits
   ```

   The compiler folds the expression at build time, so this costs nothing
   at runtime and keeps the provenance in the source.
3. Order matters. The constant folder resolves references to *previously
   defined* names only.
4. Add it to `__init__.py` (import and `__all__`) and to `__post__.py`.
5. Add a test asserting its defining relation, not just its decimal. The
   scipy sweep picks the constant up automatically.
6. Note the reference source in `docs/accuracy.md` if the group is new.

## Adding a kernel

Kernels are `@vectorize` functions over scalar dtypes:

```python
from postyp import f64
from postpyc import vectorize

@vectorize
def my_kernel(x: f64) -> f64:
    """One line saying what it computes."""
    return x * 2.0
```

Every kernel needs tests in all three modes:

- interpreted, importing from the **defining module**
  (`from ppconstants._conversions import ...`), never from the package,
  because the package swaps in native ufuncs when they are available;
- C ABI, in `tests/test_native_abi.py`, called through `pp_<name>`;
- compiled ufunc, in `tests/test_native_ext.py`, compared against
  interpreted mode.

## When the compiler gets in your way

File it upstream. That is the point of the package, not a detour
(PostSciPy working rule 2).

1. Cut the failure down to the smallest file that still shows it.
2. Record what interpreted mode does, what compiled mode does, and the
   exact error or wrong value. If it compiles but is wrong, include the
   generated C.
3. Write it up in `docs/upstream/NN-short-name.md` following the existing
   drafts: summary, reproducer, observed, cause, suggested resolution,
   environment.
4. Reference it from the relevant ROADMAP target.
5. If the workaround changes the public API, document the divergence in
   `docs/accuracy.md`.

Do **not** silently work around a compiler bug. The three existing drafts
in `docs/upstream/` are the model.

## Landing a change

Small, reviewable PRs, one target at a time. Before marking a ROADMAP
target `Done`, publish:

- the source and tests,
- interpreted test output and native build output,
- the postpython commit hash used for verification,
- any upstream finding the work produced,
- the README and ROADMAP status updates.

A claim about compiled behaviour without a commit hash is not verifiable,
so it does not count.
