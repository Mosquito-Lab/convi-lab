"""
The package as a whole: its public surface, its version, a clean import, and the import layering.
"""

import ast
import importlib.metadata
import subprocess
import sys
from pathlib import Path

import convi_lab

SOURCE = Path(convi_lab.__file__).parent

LAYERS = [  # Lowest first. A module may import from its own layer and the ones before it.
    ["convi_lab.kernel"],
    ["convi_lab.conversions.convert_clock_format", "convi_lab.conversions.convert_name"],
    ["convi_lab.parsers"],
    ["convi_lab.conversions.convert_datetime"],
]
TOP = len(LAYERS)  # The layer of anything not listed, like the package root itself


def layer_of(module: str) -> int:
    """Return the layer index of a dotted ``convi_lab`` module name."""

    for index, prefixes in enumerate(LAYERS):
        if any(module == prefix or module.startswith(f"{prefix}.") for prefix in prefixes):
            return index
    return TOP


def convi_imports(path: Path, module: str) -> list[str]:
    """Return every ``convi_lab`` module that *path* imports, at any depth (lazy imports too)."""

    package = module if path.name == "__init__.py" else module.rpartition(".")[0]
    found = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            found += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            base = package.rsplit(".", node.level - 1)[0] if node.level else ""
            target = ".".join(part for part in (base, node.module) if part)
            found.append(target)
    return [name for name in found if name == "convi_lab" or name.startswith("convi_lab.")]


def test_public_names_resolve():
    """Everything in ``__all__`` can be imported from the top level."""

    for name in convi_lab.__all__:
        assert hasattr(convi_lab, name), name


def test_version_comes_from_the_metadata():
    """``__version__`` is the installed version from pyproject.toml."""

    assert convi_lab.__version__ == importlib.metadata.version("convi-lab")


def test_import_is_clean_with_warnings_as_errors():
    """Importing convi_lab raises no warning (deprecations from logger-lab included)."""

    result = subprocess.run(
        [sys.executable, "-W", "error", "-c", "import convi_lab"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_imports_point_down_the_layers():
    """
    No module imports from a layer above its own.

    Package ``__init__`` files only gather exports, so they're skipped, except the kernel's.
    """

    violations = []
    for path in SOURCE.rglob("*.py"):
        parts = path.relative_to(SOURCE.parent).with_suffix("").parts
        module = ".".join(parts[:-1] if path.name == "__init__.py" else parts)
        if path.name == "__init__.py" and module != "convi_lab.kernel":
            continue
        for imported in convi_imports(path, module):
            if layer_of(imported) > layer_of(module):
                violations.append(f"{module} imports {imported}")
    assert violations == []
