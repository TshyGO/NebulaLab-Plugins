from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLUGINS_DIR = ROOT / "plugins"

PATTERNS = [
    re.compile(r"\bos\.system\s*\("),
    re.compile(r"\bsubprocess\.\w+\s*\("),
    re.compile(r"\beval\s*\("),
    re.compile(r"\bexec\s*\("),
    re.compile(r"__import__\s*\("),
    re.compile(r"\bopen\s*\([^#\n]*['\"](?:w|wb|a|ab|x|xb|w\+|a\+|x\+)['\"]"),
]


def iter_python_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.py")
        if "__pycache__" not in path.parts
    )


def main() -> int:
    found_dangerous = False
    for path in iter_python_files(PLUGINS_DIR):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

        for line_no, line in enumerate(lines, start=1):
            for pattern in PATTERNS:
                if pattern.search(line):
                    print(
                        f"❌ ERROR: Potentially dangerous call found in {path.as_posix()}:{line_no}: {line.strip()}",
                        file=sys.stderr,
                    )
                    found_dangerous = True
                    break

    if found_dangerous:
        print(
            "❌ Dangerous code patterns detected. CI validation failed.",
            file=sys.stderr,
        )
        return 1

    print("✅ No dangerous code patterns found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
