from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass
class ParsedImportResult:
    df: pd.DataFrame
    sample_name: str
    meta: dict[str, Any] = field(default_factory=dict)
    extra_tables: dict[str, pd.DataFrame] = field(default_factory=dict)


def _read_workbook(file_path: str | Path, *, nrows: int | None = None) -> pd.DataFrame:
    try:
        return pd.read_excel(file_path, sheet_name=0, header=None, nrows=nrows)
    except Exception as exc:
        raise ValueError(f"Failed to read TriStar workbook: {exc}") from exc


def detect_tristar_file(file_path: str | Path) -> bool:
    try:
        preview = _read_workbook(file_path, nrows=3)
    except ValueError:
        return False
    text = " ".join(str(value) for value in preview.to_numpy().ravel() if pd.notna(value))
    return "TriStar II Plus" in text


def _clean_text(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _number_from_text(value: Any) -> float | None:
    text = _clean_text(value)
    if not text:
        return None
    match = re.search(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", text)
    if not match:
        return None
    return float(match.group(0))


def _find_value_right_of(df: pd.DataFrame, labels: tuple[str, ...], *, max_offset: int = 4) -> Any:
    for row in range(df.shape[0]):
        for col in range(df.shape[1] - 1):
            text = _clean_text(df.iat[row, col])
            if any(label in text for label in labels):
                for offset in range(1, max_offset + 1):
                    if col + offset >= df.shape[1]:
                        break
                    value = df.iat[row, col + offset]
                    if pd.notna(value) and _clean_text(value) not in {"", "|"}:
                        return value
    return None


def _find_number_near_label(df: pd.DataFrame, labels: tuple[str, ...]) -> float | None:
    for row in range(df.shape[0]):
        for col in range(df.shape[1] - 1):
            text = _clean_text(df.iat[row, col])
            if not any(label in text for label in labels):
                continue
            for row_offset in range(0, 3):
                scan_row = row + row_offset
                if scan_row >= df.shape[0]:
                    break
                for scan_col in range(col + 1, min(col + 5, df.shape[1])):
                    value_text = _clean_text(df.iat[scan_row, scan_col])
                    if value_text == "|":
                        break
                    value = _number_from_text(value_text)
                    if value is not None:
                        return value
    return None


def _find_first_text(df: pd.DataFrame, pattern: str) -> str | None:
    for value in df.to_numpy().ravel():
        text = _clean_text(value)
        if pattern in text:
            return text
    return None


def _find_cell_containing(df: pd.DataFrame, text: str) -> tuple[int, int] | None:
    for row in range(df.shape[0]):
        for col in range(df.shape[1]):
            if text in _clean_text(df.iat[row, col]):
                return row, col
    return None


def _extract_metadata(df: pd.DataFrame) -> dict[str, Any]:
    instrument = _find_first_text(df, "TriStar II Plus") or "TriStar II Plus"
    sample_name = _clean_text(_find_value_right_of(df, ("Sample:",))) or "TriStar Sample"

    meta: dict[str, Any] = {
        "instrument": instrument,
        "sample_name": sample_name,
    }

    scalar_fields = {
        "sample_mass_g": ("Sample mass:",),
        "bath_temp_K": ("Analysis bath temp.:",),
        "bet_surface_area_m2g": ("BET 表面积:", "BET surface area:"),
        "single_point_surface_area_m2g": ("单点表面积", "Single point surface area"),
        "total_pore_volume_cm3g": ("总孔容", "Total pore volume"),
        "mean_pore_diameter_adsorption_A": ("吸附平均孔径", "Adsorption average pore diameter"),
        "mean_pore_diameter_desorption_A": ("脱附平均孔径", "Desorption average pore diameter"),
    }
    for key, labels in scalar_fields.items():
        value = _find_number_near_label(df, labels)
        if value is not None:
            meta[key] = value

    adsorbate = _find_value_right_of(df, ("Analysis adsorptive:",))
    if adsorbate is not None:
        meta["adsorbate"] = _clean_text(adsorbate)

    analysis_start = _find_value_right_of(df, ("开始的:", "Started:"))
    if analysis_start is not None:
        meta["analysis_start"] = _clean_text(analysis_start)

    return meta


def _coerce_pair(df: pd.DataFrame, row: int, pressure_col: int, quantity_col: int) -> tuple[float, float] | None:
    pressure = pd.to_numeric(df.iat[row, pressure_col], errors="coerce")
    quantity = pd.to_numeric(df.iat[row, quantity_col], errors="coerce")
    if pd.isna(pressure) or pd.isna(quantity):
        return None
    return float(pressure), float(quantity)


def _extract_isotherm(df: pd.DataFrame) -> pd.DataFrame:
    title_cell = _find_cell_containing(df, "等温线线性图")
    if title_cell is None:
        title_cell = _find_cell_containing(df, "Isotherm Linear Plot")
    if title_cell is None:
        raise ValueError("TriStar isotherm section was not found")

    title_row, start_col = title_cell
    header_row = None
    for row in range(title_row + 1, min(title_row + 12, df.shape[0])):
        if "相对压力" in _clean_text(df.iat[row, start_col]):
            header_row = row
            break
    if header_row is None:
        raise ValueError("TriStar isotherm header was not found")

    adsorption_rows: list[dict[str, Any]] = []
    desorption_rows: list[dict[str, Any]] = []
    for row in range(header_row + 1, df.shape[0]):
        adsorption = _coerce_pair(df, row, start_col, start_col + 1)
        desorption = _coerce_pair(df, row, start_col + 2, start_col + 3)
        if adsorption is None and desorption is None:
            if adsorption_rows or desorption_rows:
                break
            continue
        if adsorption is not None:
            adsorption_rows.append(
                {
                    "p_over_p0": adsorption[0],
                    "quantity_adsorbed": adsorption[1],
                    "branch": "adsorption",
                }
            )
        if desorption is not None:
            desorption_rows.append(
                {
                    "p_over_p0": desorption[0],
                    "quantity_adsorbed": desorption[1],
                    "branch": "desorption",
                }
            )

    rows = adsorption_rows + desorption_rows
    if not rows:
        raise ValueError("TriStar isotherm section did not contain numeric data")
    return pd.DataFrame(rows, columns=["p_over_p0", "quantity_adsorbed", "branch"])


def parse_tristar_file(file_path: str | Path) -> ParsedImportResult:
    df = _read_workbook(file_path)
    if not detect_tristar_file(file_path):
        raise ValueError("File does not look like a TriStar II Plus workbook")

    meta = _extract_metadata(df)
    isotherm = _extract_isotherm(df)
    return ParsedImportResult(
        df=isotherm,
        sample_name=str(meta.get("sample_name") or "TriStar Sample"),
        meta=meta,
        extra_tables={},
    )
