from __future__ import annotations

from pathlib import Path

from .compat import ImportResult, register_importer
from .parser import detect_thermo_kalpha_xps_file, parse_thermo_kalpha_workbook

# Import operation module for decorator registration.
from . import processing as _processing  # noqa: F401


@register_importer(
    id="xps-thermo-kalpha",
    name="Thermo Scientific K-Alpha XPS",
    extensions=[".xls", ".xlsx"],
    description="Parse Thermo Scientific K-Alpha / Avantage XPS Excel exports into per-sheet data items.",
    category="instrument",
    min_app_version="0.8.0",
    detect_fn=detect_thermo_kalpha_xps_file,
)
def parse(file_path: str | Path) -> ImportResult:
    result = parse_thermo_kalpha_workbook(file_path)
    return ImportResult(
        df=result.df,
        sample_name=result.sample_name,
        meta=result.meta,
        extra_tables=result.extra_tables,
    )