"""Structural invariants of the package layout.

`__init__.py` is the Python namespace manifest and additionally imports
`_codata`, which is not POST Python. `__post__.py` is the compiler's entry
point and must re-export exactly the POST modules. That split is
load-bearing — if the two drift apart, the compiled artifact silently
stops matching the Python API — and nothing else checks it.
"""

import ast
from pathlib import Path

import ppconstants

PACKAGE_DIR = Path(ppconstants.__file__).parent
POST_MODULES = ["_mathematical", "_physical", "_prefixes", "_units", "_conversions"]


def _imports_by_module(path):
    """Map 'ppconstants._x' -> {names imported from it} for a source file."""
    tree = ast.parse(path.read_text(), filename=str(path))
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            found.setdefault(node.module, set()).update(
                alias.name for alias in node.names
            )
    return found


def test_post_entry_exists():
    assert (PACKAGE_DIR / "__post__.py").is_file()


def test_post_entry_and_manifest_agree_on_post_modules():
    init = _imports_by_module(PACKAGE_DIR / "__init__.py")
    post = _imports_by_module(PACKAGE_DIR / "__post__.py")
    for module in POST_MODULES:
        key = f"ppconstants.{module}"
        assert key in init, f"{module} missing from __init__.py"
        assert key in post, f"{module} missing from __post__.py"
        assert init[key] == post[key], (
            f"__init__.py and __post__.py disagree on {module}: "
            f"only in __init__={sorted(init[key] - post[key])}, "
            f"only in __post__={sorted(post[key] - init[key])}"
        )


def test_post_entry_excludes_interpreted_only_modules():
    post = _imports_by_module(PACKAGE_DIR / "__post__.py")
    assert "ppconstants._codata" not in post, (
        "_codata is CPython-boundary code and must not reach the compiler"
    )


def test_manifest_includes_the_interpreted_only_module():
    init = _imports_by_module(PACKAGE_DIR / "__init__.py")
    assert "ppconstants._codata" in init


def test_build_scripts_target_the_package_directory():
    """__post__.py only wins when the compiler is handed a directory."""
    for script in ("build_native.py", "build_ext.py"):
        source = (PACKAGE_DIR.parent / "scripts" / script).read_text()
        assert 'PACKAGE_ENTRY = ' in source, script
        entry_line = next(
            line for line in source.splitlines()
            if line.startswith("PACKAGE_ENTRY = ")
        )
        assert "__init__.py" not in entry_line, (
            f"{script} passes __init__.py to the compiler, which would try to "
            "compile the interpreted-only _codata module"
        )


def test_every_post_module_is_listed_in_build_native():
    source = (PACKAGE_DIR.parent / "scripts" / "build_native.py").read_text()
    for module in POST_MODULES:
        assert f'"{module}"' in source, f"{module} missing from EXPECTED_NATIVE"
