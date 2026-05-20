from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd


SCAN_SUFFIX = " Scan"
SURVEY_SHEET = "XPS Survey"
PEAK_TABLE_SHEET = "Peak Table"
TITLES_SHEET = "Titles"
MAX_CONSECUTIVE_EMPTY_ROWS = 3


@dataclass
class ParsedImportResult:
    df: pd.DataFrame
    sample_name: str
    meta: dict[str, Any] = field(default_factory=dict)
    extra_tables: dict[str, pd.DataFrame] = field(default_factory=dict)


def _clean_text(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value).replace("\ufeff", "").strip()


def _normalized_text(value: Any) -> str:
    return re.sub(r"\s+", " ", _clean_text(value)).casefold()


def _to_number(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = _clean_text(value)
    if not text:
        return None
    match = re.search(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", text)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def _read_workbook(file_path: str | Path) -> dict[str, pd.DataFrame]:
    try:
        sheets = pd.read_excel(file_path, sheet_name=None, header=None)
    except Exception as exc:
        raise ValueError(f"Failed to read Thermo K-Alpha XPS workbook: {exc}") from exc
    return {str(name): df for name, df in sheets.items()}


def _sheet_looks_like_scan(sheet_name: str) -> bool:
    return sheet_name == SURVEY_SHEET or sheet_name.endswith(SCAN_SUFFIX)


def _find_cell_containing(df: pd.DataFrame, needle: str) -> tuple[int, int] | None:
    target = needle.casefold()
    for row in range(df.shape[0]):
        for col in range(df.shape[1]):
            if target in _normalized_text(df.iat[row, col]):
                return row, col
    return None


def _find_scan_header(df: pd.DataFrame) -> tuple[int, int] | None:
    return _find_cell_containing(df, "Binding Energy")


def _has_counts_unit_nearby(df: pd.DataFrame, header_row: int) -> bool:
    for row in range(header_row, min(header_row + 3, df.shape[0])):
        for col in range(df.shape[1]):
            if "counts" in _normalized_text(df.iat[row, col]):
                return True
    return False


def detect_thermo_kalpha_xps_file(file_path: str | Path) -> bool:
    path = Path(file_path)
    if path.suffix.lower() not in {".xls", ".xlsx"}:
        return False

    try:
        workbook = _read_workbook(path)
    except ValueError:
        return False

    sheet_names = list(workbook.keys())
    score = 0
    if SURVEY_SHEET in sheet_names:
        score += 1
    if PEAK_TABLE_SHEET in sheet_names:
        score += 1
    if any(name.endswith(SCAN_SUFFIX) for name in sheet_names):
        score += 1

    for name, df in workbook.items():
        if not _sheet_looks_like_scan(name):
            continue
        header = _find_scan_header(df)
        if header is not None and _has_counts_unit_nearby(df, header[0]):
            score += 2
            break

    flat_text = " ".join(
        _clean_text(value)
        for df in workbook.values()
        for value in df.head(20).to_numpy().ravel()
        if pd.notna(value)
    )
    if "Al K Alpha" in flat_text or "K-Alpha" in flat_text or "K Alpha" in flat_text:
        score += 1

    return score >= 3


def _find_intensity_columns(df: pd.DataFrame, header_row: int, energy_col: int) -> tuple[int, int | None]:
    unit_row = header_row + 1 if header_row + 1 < df.shape[0] else header_row
    counts_columns: list[int] = []
    for col in range(energy_col + 1, df.shape[1]):
        if "counts" in _normalized_text(df.iat[unit_row, col]):
            counts_columns.append(col)

    if not counts_columns:
        # Thermo Avantage exports commonly use empty spacer columns:
        # col 0 = Binding Energy, col 2 = CPS, col 4 = background CPS.
        intensity_col = energy_col + 2 if energy_col + 2 < df.shape[1] else energy_col + 1
        background_col = energy_col + 4 if energy_col + 4 < df.shape[1] else None
        return intensity_col, background_col

    intensity_col = counts_columns[0]
    background_col = None
    for col in counts_columns[1:]:
        header_text = _normalized_text(df.iat[header_row, col])
        if "back" in header_text or "bg" in header_text:
            background_col = col
            break
    if background_col is None and len(counts_columns) > 1:
        background_col = counts_columns[1]
    return intensity_col, background_col


def parse_scan_sheet(df: pd.DataFrame, *, sheet_name: str, source_file: str) -> pd.DataFrame:
    header = _find_scan_header(df)
    if header is None:
        raise ValueError(f"Sheet '{sheet_name}' does not contain a Binding Energy header")

    header_row, energy_col = header
    intensity_col, background_col = _find_intensity_columns(df, header_row, energy_col)
    if intensity_col >= df.shape[1]:
        raise ValueError(f"Sheet '{sheet_name}' does not contain an intensity column")

    rows: list[dict[str, Any]] = []
    empty_run = 0
    for row in range(header_row + 2, df.shape[0]):
        energy = _to_number(df.iat[row, energy_col])
        intensity = _to_number(df.iat[row, intensity_col])
        background = _to_number(df.iat[row, background_col]) if background_col is not None and background_col < df.shape[1] else None

        if energy is None or intensity is None:
            if rows:
                empty_run += 1
                if empty_run >= MAX_CONSECUTIVE_EMPTY_ROWS:
                    break
            continue

        empty_run = 0
        background_value = background if background is not None else pd.NA
        corrected = intensity - (background or 0.0)
        rows.append(
            {
                "binding_energy_eV": energy,
                "intensity_cps": intensity,
                "background_cps": background_value,
                "corrected_intensity_cps": corrected,
                "source_sheet": sheet_name,
                "source_file": source_file,
            }
        )

    if not rows:
        raise ValueError(f"Sheet '{sheet_name}' did not contain numeric XPS scan data")
    return pd.DataFrame(
        rows,
        columns=[
            "binding_energy_eV",
            "intensity_cps",
            "background_cps",
            "corrected_intensity_cps",
            "source_sheet",
            "source_file",
        ],
    )


def _normalize_metadata_key(label: str) -> str:
    key = re.sub(r"[^0-9A-Za-z]+", "_", label.strip().lower()).strip("_")
    aliases = {
        "total_acquisition_time": "total_acquisition_time",
        "number_of_scans": "number_of_scans",
        "source_gun_type": "source_gun_type",
        "spot_size": "spot_size",
        "lens_mode": "lens_mode",
        "analyser_mode": "analyser_mode",
        "analyzer_mode": "analyser_mode",
        "energy_step_size": "energy_step_size",
        "number_of_energy_steps": "number_of_energy_steps",
    }
    return aliases.get(key, key)


def extract_region_metadata(df: pd.DataFrame) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    anchor = _find_cell_containing(df, "Acquisition Parameters")
    if anchor is None:
        return metadata

    start_row, start_col = anchor
    for row in range(start_row + 1, min(start_row + 40, df.shape[0])):
        label = _clean_text(df.iat[row, start_col]) if start_col < df.shape[1] else ""
        if not label or label.casefold() in {"parameter", "parameters"}:
            continue
        value = None
        for col in range(start_col + 1, min(start_col + 4, df.shape[1])):
            candidate = df.iat[row, col]
            if pd.notna(candidate) and _clean_text(candidate):
                value = _clean_text(candidate)
                break
        if value is None:
            continue
        key = _normalize_metadata_key(label)
        metadata[key] = value

    analyser = str(metadata.get("analyser_mode", ""))
    pass_energy_match = re.search(r"pass\s+energy\s+([-+]?\d+(?:\.\d+)?)", analyser, flags=re.I)
    if pass_energy_match:
        metadata["pass_energy_eV"] = float(pass_energy_match.group(1))

    step_size = _to_number(metadata.get("energy_step_size"))
    if step_size is not None:
        metadata["energy_step_size_eV"] = step_size

    scans = _to_number(metadata.get("number_of_scans"))
    if scans is not None:
        metadata["number_of_scans"] = int(scans)

    steps = _to_number(metadata.get("number_of_energy_steps"))
    if steps is not None:
        metadata["number_of_energy_steps"] = int(steps)

    return metadata


PEAK_COLUMN_ALIASES: dict[str, str] = {
    "name": "name",
    "start be": "start_be_eV",
    "peak be": "peak_be_eV",
    "end be": "end_be_eV",
    "height cps": "height_cps",
    "fwhm ev": "fwhm_eV",
    "area p cps ev": "area_p_cps_eV",
    "area p": "area_p_cps_eV",
    "area n tpp2m": "area_n_tpp2m",
    "area n": "area_n_tpp2m",
    "atomic %": "atomic_percent",
    "atomic": "atomic_percent",
    "title": "title",
    "file name": "file_name",
}


def _normalize_peak_header(value: Any) -> str:
    text = _clean_text(value).replace("/", " ").replace(".", " ")
    text = re.sub(r"\s+", " ", text).strip().casefold()
    return text


def parse_peak_table(df: pd.DataFrame) -> pd.DataFrame | None:
    header_row = None
    for row in range(min(df.shape[0], 40)):
        headers = [_normalize_peak_header(df.iat[row, col]) for col in range(df.shape[1])]
        if "name" in headers and any("peak be" in header for header in headers):
            header_row = row
            break
    if header_row is None:
        return None

    column_map: dict[int, str] = {}
    used_names: set[str] = set()
    for col in range(df.shape[1]):
        normalized = _normalize_peak_header(df.iat[header_row, col])
        target = PEAK_COLUMN_ALIASES.get(normalized)
        if target and target not in used_names:
            column_map[col] = target
            used_names.add(target)

    if not column_map:
        return None

    rows: list[dict[str, Any]] = []
    empty_run = 0
    for row in range(header_row + 1, df.shape[0]):
        record: dict[str, Any] = {}
        has_value = False
        for col, target in column_map.items():
            value = df.iat[row, col]
            if pd.notna(value) and _clean_text(value):
                has_value = True
            if target.endswith("_eV") or target.endswith("_cps") or target == "atomic_percent" or target.endswith("tpp2m"):
                record[target] = _to_number(value)
            else:
                record[target] = _clean_text(value) if pd.notna(value) else ""
        if not has_value:
            if rows:
                empty_run += 1
                if empty_run >= MAX_CONSECUTIVE_EMPTY_ROWS:
                    break
            continue
        empty_run = 0
        rows.append(record)

    if not rows:
        return None
    preferred = [
        "name",
        "start_be_eV",
        "peak_be_eV",
        "end_be_eV",
        "height_cps",
        "fwhm_eV",
        "area_p_cps_eV",
        "area_n_tpp2m",
        "atomic_percent",
        "title",
        "file_name",
    ]
    columns = [column for column in preferred if column in used_names]
    return pd.DataFrame(rows, columns=columns)


def _clean_generic_sheet(df: pd.DataFrame, *, source_sheet: str, source_file: str) -> pd.DataFrame | None:
    cleaned = df.dropna(how="all").dropna(axis=1, how="all")
    if cleaned.empty:
        return None
    cleaned = cleaned.reset_index(drop=True).copy()
    cleaned.columns = [f"column_{index + 1}" for index in range(cleaned.shape[1])]
    cleaned["source_sheet"] = source_sheet
    cleaned["source_file"] = source_file
    return cleaned


def parse_thermo_kalpha_workbook(file_path: str | Path) -> ParsedImportResult:
    path = Path(file_path)
    workbook = _read_workbook(path)
    if not detect_thermo_kalpha_xps_file(path):
        raise ValueError("File does not look like a Thermo Scientific K-Alpha XPS workbook")

    scan_tables: dict[str, pd.DataFrame] = {}
    region_metadata: dict[str, dict[str, Any]] = {}
    for sheet_name, df in workbook.items():
        if not _sheet_looks_like_scan(sheet_name):
            continue
        try:
            scan_tables[sheet_name] = parse_scan_sheet(df, sheet_name=sheet_name, source_file=path.name)
            region_metadata[sheet_name] = extract_region_metadata(df)
        except ValueError:
            continue

    if not scan_tables:
        raise ValueError("Thermo K-Alpha workbook did not contain any numeric XPS scan sheets")

    main_sheet = next(iter(scan_tables.keys()))
    sample_stem = path.stem
    extra_tables: dict[str, pd.DataFrame] = {}
    for sheet_name, table in scan_tables.items():
        if sheet_name != main_sheet:
            extra_tables[sheet_name] = table

    peak_table = parse_peak_table(workbook[PEAK_TABLE_SHEET]) if PEAK_TABLE_SHEET in workbook else None
    if peak_table is not None and not peak_table.empty:
        extra_tables[PEAK_TABLE_SHEET] = peak_table

    titles_table = _clean_generic_sheet(workbook[TITLES_SHEET], source_sheet=TITLES_SHEET, source_file=path.name) if TITLES_SHEET in workbook else None
    if titles_table is not None and not titles_table.empty:
        extra_tables[TITLES_SHEET] = titles_table

    source_gun_type = next(
        (
            str(meta.get("source_gun_type"))
            for meta in region_metadata.values()
            if meta.get("source_gun_type")
        ),
        None,
    )
    meta = {
        "instrument_family": "Thermo Scientific K-Alpha",
        "source_file": path.name,
        "sheet_names": list(workbook.keys()),
        "main_sheet": main_sheet,
        "scan_sheets": list(scan_tables.keys()),
        "peak_table_available": peak_table is not None and not peak_table.empty,
        "titles_sheet_available": titles_table is not None and not titles_table.empty,
        "region_metadata": region_metadata,
    }
    if source_gun_type:
        meta["source_gun_type"] = source_gun_type

    return ParsedImportResult(
        df=scan_tables[main_sheet],
        sample_name=f"{sample_stem} · {main_sheet}",
        meta=meta,
        extra_tables=extra_tables,
    )