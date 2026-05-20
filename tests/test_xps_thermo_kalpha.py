from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from plugins.official.xps_thermo_kalpha.parser import (  # noqa: E402
    detect_thermo_kalpha_xps_file,
    parse_thermo_kalpha_workbook,
)


def _scan_sheet(start_energy: float, sheet_name: str) -> pd.DataFrame:
    df = pd.DataFrame([[None for _ in range(13)] for _ in range(24)])
    df.iat[0, 7] = "Acquisition Parameters :"
    df.iat[2, 7] = "Parameter"
    df.iat[3, 7] = "Total acquisition time"
    df.iat[3, 8] = "47.8 secs"
    df.iat[4, 7] = "Number of Scans"
    df.iat[4, 8] = "5"
    df.iat[5, 7] = "Source Gun Type"
    df.iat[5, 8] = "Al K Alpha"
    df.iat[8, 7] = "Analyser Mode"
    df.iat[8, 8] = "CAE : Pass Energy 50.0 eV"
    df.iat[9, 7] = "Energy Step Size"
    df.iat[9, 8] = "0.100 eV"
    df.iat[10, 7] = "Number of Energy Steps"
    df.iat[10, 8] = "191"

    df.iat[14, 0] = "Binding Energy (E)"
    df.iat[14, 4] = "Backgnd."
    df.iat[15, 0] = "eV"
    df.iat[15, 2] = "Counts / s"
    df.iat[15, 4] = "Counts / s"
    df.iat[16, 0] = start_energy
    df.iat[16, 2] = 4983.11
    df.iat[16, 4] = 0
    df.iat[17, 0] = start_energy - 0.1
    df.iat[17, 2] = 4793.57
    df.iat[17, 4] = 4893.25
    df.iat[18, 0] = start_energy - 0.2
    df.iat[18, 2] = 5000.0
    df.iat[18, 4] = 4900.0
    df.iat[20, 0] = None
    df.iat[20, 2] = None
    df.iat[22, 0] = f"end {sheet_name}"
    return df


def _peak_table() -> pd.DataFrame:
    df = pd.DataFrame([[None for _ in range(12)] for _ in range(6)])
    headers = ["Name", "Start BE", "Peak BE", "End BE", "Height CPS", "FWHM eV", "Atomic %", "Title", "File Name"]
    for index, header in enumerate(headers):
        df.iat[1, index] = header
    df.iloc[2, :9] = ["C1s", 297.9, 284.32, 279.1, 27591.07, 3.05, 60.11, "C1s Scan", "C1s Scan.VGD"]
    df.iloc[3, :9] = ["O1s", 544.9, 531.48, 525.1, 35941.88, 2.07, 26.95, "O1s Scan", "O1s Scan.VGD"]
    return df


def _write_xps_fixture(path: Path) -> None:
    with pd.ExcelWriter(path) as writer:
        _scan_sheet(1045.0, "Zn2p Scan").to_excel(writer, sheet_name="Zn2p Scan", index=False, header=False)
        _scan_sheet(1360.0, "XPS Survey").to_excel(writer, sheet_name="XPS Survey", index=False, header=False)
        _scan_sheet(298.0, "C1s Scan").to_excel(writer, sheet_name="C1s Scan", index=False, header=False)
        _peak_table().to_excel(writer, sheet_name="Peak Table", index=False, header=False)
        pd.DataFrame([["C1s Scan", "C1s Scan.VGD"], ["O1s Scan", "O1s Scan.VGD"]]).to_excel(writer, sheet_name="Titles", index=False, header=False)


def test_detect_thermo_kalpha_xps_file_identifies_workbook(tmp_path: Path) -> None:
    path = tmp_path / "xps.xlsx"
    _write_xps_fixture(path)

    assert detect_thermo_kalpha_xps_file(path) is True


def test_detect_thermo_kalpha_xps_file_rejects_unrelated_workbook(tmp_path: Path) -> None:
    path = tmp_path / "other.xlsx"
    pd.DataFrame([["Other Instrument"]]).to_excel(path, index=False, header=False)

    assert detect_thermo_kalpha_xps_file(path) is False


def test_parse_thermo_kalpha_workbook_returns_per_sheet_tables(tmp_path: Path) -> None:
    path = tmp_path / "1.xlsx"
    _write_xps_fixture(path)

    result = parse_thermo_kalpha_workbook(path)

    assert result.sample_name == "1 · Zn2p Scan"
    assert list(result.df.columns) == [
        "binding_energy_eV",
        "intensity_cps",
        "background_cps",
        "corrected_intensity_cps",
        "source_sheet",
        "source_file",
    ]
    assert result.df["source_sheet"].unique().tolist() == ["Zn2p Scan"]
    assert result.df["binding_energy_eV"].tolist() == [1045.0, 1044.9, 1044.8]
    assert pytest.approx(result.df.loc[1, "corrected_intensity_cps"]) == -99.68

    assert "XPS Survey" in result.extra_tables
    assert "C1s Scan" in result.extra_tables
    assert result.extra_tables["C1s Scan"]["source_sheet"].unique().tolist() == ["C1s Scan"]
    assert "Peak Table" in result.extra_tables
    assert "Titles" in result.extra_tables


def test_parse_thermo_kalpha_workbook_extracts_peak_table_and_metadata(tmp_path: Path) -> None:
    path = tmp_path / "1.xlsx"
    _write_xps_fixture(path)

    result = parse_thermo_kalpha_workbook(path)

    peak_table = result.extra_tables["Peak Table"]
    assert peak_table.to_dict(orient="records")[:1] == [
        {
            "name": "C1s",
            "start_be_eV": 297.9,
            "peak_be_eV": 284.32,
            "end_be_eV": 279.1,
            "height_cps": 27591.07,
            "fwhm_eV": 3.05,
            "atomic_percent": 60.11,
            "title": "C1s Scan",
            "file_name": "C1s Scan.VGD",
        }
    ]
    assert result.meta["source_gun_type"] == "Al K Alpha"
    assert result.meta["main_sheet"] == "Zn2p Scan"
    assert result.meta["scan_sheets"] == ["Zn2p Scan", "XPS Survey", "C1s Scan"]
    assert result.meta["region_metadata"]["C1s Scan"]["number_of_scans"] == 5
    assert result.meta["region_metadata"]["C1s Scan"]["pass_energy_eV"] == 50.0
    assert result.meta["region_metadata"]["C1s Scan"]["energy_step_size_eV"] == 0.1


def test_parse_thermo_kalpha_workbook_raises_for_missing_scan_data(tmp_path: Path) -> None:
    path = tmp_path / "bad.xlsx"
    with pd.ExcelWriter(path) as writer:
        pd.DataFrame([["Peak Table"], ["No scan data"]]).to_excel(writer, sheet_name="Peak Table", index=False, header=False)
        df = pd.DataFrame([[None for _ in range(5)] for _ in range(4)])
        df.iat[0, 0] = "Binding Energy (E)"
        df.iat[1, 0] = "eV"
        df.iat[1, 2] = "Counts / s"
        df.iat[2, 2] = "Al K Alpha"
        df.to_excel(writer, sheet_name="XPS Survey", index=False, header=False)

    with pytest.raises(ValueError, match="numeric XPS scan"):
        parse_thermo_kalpha_workbook(path)