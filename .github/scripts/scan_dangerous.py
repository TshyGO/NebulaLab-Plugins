from __future__ import annotations

import re
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


def main() -> None:
    for path in iter_python_files(PLUGINS_DIR):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

        for line_no, line in enumerate(lines, start=1):
            for pattern in PATTERNS:
                if pattern.search(line):
                    print(
                        f"⚠️  WARNING: Potentially dangerous call found in {path.as_posix()}:{line_no}: {line.strip()}"
                    )
                    break


if __name__ == "__main__":
    main()
