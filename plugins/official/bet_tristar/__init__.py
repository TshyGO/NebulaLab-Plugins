from __future__ import annotations

import sys
from pathlib import Path


def _ensure_nebula_sdk_importable() -> None:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "nebula_sdk").is_dir() or (parent / "nebula_sdk.py").is_file():
            parent_str = str(parent)
            if parent_str not in sys.path:
                sys.path.insert(0, parent_str)
            return

try:
    from nebula_sdk import ImportResult, register_importer
except ImportError:
    _ensure_nebula_sdk_importable()
    from nebula_sdk import ImportResult, register_importer

from .parser import detect_tristar_file, parse_tristar_file


@register_importer(
    id="bet-tristar",
    name="BET TriStar II Plus",
    extensions=[".xls"],
    description="Parse Micromeritics TriStar II Plus BET analysis reports.",
    category="instrument",
    min_app_version="0.8.0",
    detect_fn=detect_tristar_file,
)
def parse(file_path: str | Path) -> ImportResult:
    result = parse_tristar_file(file_path)
    return ImportResult(
        df=result.df,
        sample_name=result.sample_name,
        meta=result.meta,
        extra_tables=result.extra_tables,
    )
