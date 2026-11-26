#!/usr/bin/env python3
"""
Guardrail for the `main` branch (`make check-main`).

Verifies that:
  1. Every CPU exercise stub in exercises/*/*.py still raises NotImplementedError
     in every function/method (preventing accidental solution commits to main).
  2. Every stub has a matching test_<module>.py file next to it.
  3. Every exercise module name is unique repo-wide and no __init__.py exists
     inside exercises/.

Exits 1 if any check fails.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EX_ROOT = ROOT / "exercises"


def _raises_not_implemented(node: ast.AST) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Raise) and child.exc is not None:
            exc = child.exc
            if isinstance(exc, ast.Name) and exc.id == "NotImplementedError":
                return True
            if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name) and exc.func.id == "NotImplementedError":
                return True
    return False


def main() -> int:
    errors: list[str] = []
    if not EX_ROOT.is_dir():
        print("FAIL: exercises/ directory not found")
        return 1

    for init_file in sorted(EX_ROOT.rglob("__init__.py")):
        errors.append(f"forbidden __init__.py inside exercises/: {init_file.relative_to(ROOT)}")

    seen_mods: dict[str, Path] = {}
    stub_count = 0
    fn_count = 0

    for stub in sorted(EX_ROOT.glob("*/*.py")):
        if stub.name.startswith(("test_", "_")) or stub.name == "conftest.py":
            continue
        stub_count += 1
        rel = stub.relative_to(ROOT)
        mod = stub.stem
        if mod in seen_mods:
            errors.append(f"duplicate exercise module {mod}: {seen_mods[mod]} and {rel}")
        seen_mods[mod] = rel

        test_file = stub.parent / f"test_{mod}.py"
        if not test_file.is_file():
            errors.append(f"missing test suite {test_file.relative_to(ROOT)} for {rel}")

        src = stub.read_text(encoding="utf-8")
        try:
            tree = ast.parse(src, filename=str(rel))
        except SyntaxError as exc:
            errors.append(f"syntax error in {rel}: {exc}")
            continue

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn_count += 1
                if not _raises_not_implemented(node):
                    errors.append(f"{rel}:{node.lineno} `{node.name}` does not raise NotImplementedError (keep solutions off main!)")
            elif isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        fn_count += 1
                        if not _raises_not_implemented(item):
                            errors.append(
                                f"{rel}:{item.lineno} `{node.name}.{item.name}` does not raise NotImplementedError (keep solutions off main!)"
                            )

    if errors:
        print(f"✗ main stub guardrail failed ({len(errors)} issue(s)):")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"✓ main stubs clean: {stub_count} exercise modules ({fn_count} functions/methods raise NotImplementedError)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
