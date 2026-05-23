from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .compat import ImportResult, register_importer
from .parser import detect_thermo_kalpha_xps_file, parse_thermo_kalpha_workbook

# Import operation module for decorator registration.
from . import processing as _processing  # noqa: F401


def _clean_name(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).replace("\ufeff", "").strip().split())


DISPLAY_NAME_SEPARATOR = "·"


def _table_display_name(base_name: str, table_name: str, separator: str = DISPLAY_NAME_SEPARATOR) -> str:
    table_label = _clean_name(table_name)
    if not table_label:
        return base_name
    if table_label.startswith(f"{base_name}{separator}"):
        return table_label
    return f"{base_name}{separator}{table_label}"


def _infer_main_table_name(result: Any) -> str:
    meta = getattr(result, "meta", None)
    if isinstance(meta, dict):
        for key in ("main_sheet", "main_table", "source_sheet"):
            value = _clean_name(meta.get(key))
            if value:
                return value

    df = getattr(result, "df", None)
    if isinstance(df, pd.DataFrame) and not df.empty:
        for column in ("source_sheet", "source_table"):
            if column in df.columns:
                series = df[column].dropna()
                if not series.empty:
                    value = _clean_name(series.iloc[0])
                    if value:
                        return value
    return ""


def apply_grouped_table_display_names(result: Any, file_path: str | Path) -> Any:
    """Apply '<file>·<sheet>' display names to all XPS importer tables."""

    df = getattr(result, "df", None)
    if not isinstance(df, pd.DataFrame):
        return result

    path = Path(file_path)
    base_name = _clean_name(path.stem) or "Imported Data"
    extra_tables = getattr(result, "extra_tables", None) or {}
    if not isinstance(extra_tables, dict):
        extra_tables = {}

    meta = getattr(result, "meta", None)
    meta = dict(meta) if isinstance(meta, dict) else {}
    display_name_by_table = meta.get("display_name_by_table")
    display_name_by_table = dict(display_name_by_table) if isinstance(display_name_by_table, dict) else {}

    for table_name in extra_tables.keys():
        table_key = str(table_name)
        display_name_by_table[table_key] = _table_display_name(base_name, table_key)

    main_table = _infer_main_table_name(result)
    sample_name = _table_display_name(base_name, main_table) if main_table else base_name

    meta.update(
        {
            "base_sample_name": base_name,
            "display_name_by_table": display_name_by_table,
            "grouped_table_importer": {
                "applied": True,
                "separator": DISPLAY_NAME_SEPARATOR,
            },
        }
    )

    result.meta = meta
    result.sample_name = sample_name
    return result


def _metadata_table_name(sample: Any) -> str:
    analysis = getattr(sample, "analysis", None)
    if isinstance(analysis, dict):
        value = _clean_name(analysis.get("table_name"))
        if value:
            return value

    metadata = getattr(sample, "metadata", None)
    if isinstance(metadata, dict):
        importer = metadata.get("importer")
        if isinstance(importer, dict):
            value = _clean_name(importer.get("table_name"))
            if value:
                return value
        nested_analysis = metadata.get("analysis")
        if isinstance(nested_analysis, dict):
            value = _clean_name(nested_analysis.get("table_name"))
            if value:
                return value
    return ""


def _patch_nebula_importer_sample_naming() -> None:
    """Patch older Nebula Lab runtimes that ignore importer display_name_by_table metadata.

    Some app builds name importer extra tables as '<parent sample> · <table>'. For XPS
    this can produce names like '1·Zn2p Scan · XPS Survey'. The requested naming is
    always '<file>·<sheet>', so normalize generated SampleRecord names when possible.
    """

    try:
        from engine.api import routes_files
    except Exception:
        return

    original = getattr(routes_files, "_create_importer_sample_records", None)
    if not callable(original) or getattr(original, "_xps_file_sheet_name_patch", False):
        return

    def patched_create_importer_sample_records(*args: Any, **kwargs: Any):
        samples = original(*args, **kwargs)
        plugin = kwargs.get("plugin")
        result = kwargs.get("result")
        filename = str(kwargs.get("filename") or "")

        if getattr(plugin, "id", "") != "xps-thermo-kalpha" or not samples:
            return samples

        file_stem = _clean_name(Path(filename).stem) or "Imported Data"
        meta = getattr(result, "meta", None)
        meta = meta if isinstance(meta, dict) else {}
        display_name_by_table = meta.get("display_name_by_table")
        display_name_by_table = display_name_by_table if isinstance(display_name_by_table, dict) else {}

        main_name = _clean_name(getattr(result, "sample_name", ""))
        main_sheet = _clean_name(meta.get("main_sheet"))
        samples[0].name = main_name or _table_display_name(file_stem, main_sheet)

        for sample in samples[1:]:
            table_name = _metadata_table_name(sample)
            table_display_name = _clean_name(display_name_by_table.get(table_name)) if table_name else ""
            sample.name = table_display_name or _table_display_name(file_stem, table_name)

        return samples

    patched_create_importer_sample_records._xps_file_sheet_name_patch = True  # type: ignore[attr-defined]
    routes_files._create_importer_sample_records = patched_create_importer_sample_records


@register_importer(
    id="xps-thermo-kalpha",
    name="Thermo Scientific K-Alpha XPS",
    extensions=[".xls", ".xlsx"],
    description="Parse Thermo Scientific K-Alpha / Avantage XPS Excel exports into per-sheet data items with '<file>·<sheet>' display names.",
    category="instrument",
    min_app_version="0.8.0",
    detect_fn=detect_thermo_kalpha_xps_file,
)
def parse(file_path: str | Path) -> ImportResult:
    result = apply_grouped_table_display_names(parse_thermo_kalpha_workbook(file_path), file_path)
    return ImportResult(
        df=result.df,
        sample_name=result.sample_name,
        meta=result.meta,
        extra_tables=result.extra_tables,
    )


_patch_nebula_importer_sample_naming()