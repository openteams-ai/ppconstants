"""Compile each ppconstants module to a native shared library.

Every module must build (constants-only modules compile to translation
units whose constants fold into importing kernels; _conversions links
against _physical's `c` via cross-module constant import). The whole
package is also built into a single shared library from
ppconstants/__init__.py. Any failure exits non-zero.
"""

import sys
import tempfile
from pathlib import Path

from postpyc.build import build_file, BuildError

PACKAGE_DIR = Path(__file__).resolve().parent.parent / "ppconstants"
PACKAGE_ENTRY = PACKAGE_DIR  # directory entry: __post__.py takes precedence (spec §9.1)

EXPECTED_NATIVE = [
    "_mathematical",
    "_physical",
    "_prefixes",
    "_units",
    "_conversions",
]


def main() -> int:
    out_dir = Path(tempfile.mkdtemp(prefix="ppconstants-native-"))
    failures = []

    for name in EXPECTED_NATIVE:
        source = PACKAGE_DIR / f"{name}.py"
        try:
            lib = build_file(source, output=out_dir / f"{name}.so")
            print(f"  {name:13s} OK       -> {lib}")
        except BuildError as exc:
            failures.append(name)
            print(f"  {name:13s} FAILED")
            print("    " + "\n    ".join(str(exc).splitlines()[:6]))

    # The full package: one shared library with all translation units
    # plus stable C ABI sidecars (`ppconstants.h`, `ppconstants.json`).
    try:
        lib = build_file(
            PACKAGE_ENTRY,
            output=out_dir / "ppconstants.so",
            emit_header=True,
            emit_manifest=True,
        )
        print(f"  {'package':13s} OK       -> {lib}")
        print(f"  {'header':13s} OK       -> {lib.with_suffix('.h')}")
        print(f"  {'manifest':13s} OK       -> {lib.with_suffix('.json')}")
    except BuildError as exc:
        failures.append("package")
        print(f"  {'package':13s} FAILED")
        print("    " + "\n    ".join(str(exc).splitlines()[:6]))

    if failures:
        print(f"\n{len(failures)} build(s) failed: {failures}")
        return 1
    print("\nAll modules and the full package compile natively.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
