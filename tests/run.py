from __future__ import annotations

import importlib
import inspect
import pathlib
import sys
import traceback


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    failures = 0
    test_files = sorted(pathlib.Path(__file__).resolve().parent.glob("test_*.py"))
    for test_file in test_files:
        module = importlib.import_module(test_file.stem)
        for name, func in inspect.getmembers(module, inspect.isfunction):
            if not name.startswith("test_"):
                continue
            try:
                func()
                print(f"PASS {test_file.name}::{name}")
            except Exception:
                failures += 1
                print(f"FAIL {test_file.name}::{name}")
                traceback.print_exc()
    print(f"{len(test_files)} test files, {failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
