from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from plugins.official.bet_tristar.parser import detect_tristar_file, parse_tristar_file


def _write_tristar_fixture(path: Path) -> None:
    df = pd.DataFrame([[None for _ in range(100)] for _ in range(60)])
    df.iat[0, 4] = "|"
    df.iat[0, 10] = "|"

    for start in (0, 5, 11):
        df.iat[1, start] = "TriStar II Plus 3.03"
        df.iat[5, start] = "Sample:"
        df.iat[5, start + 1] = "PMSO"
        df.iat[11, start] = "开始的:"
        df.iat[11, start + 1] = "2026/4/25 21:54:32"
        df.iat[11, start + 2] = "Analysis adsorptive:"
        df.iat[11, start + 3] = "N2"
        df.iat[12, start + 2] = "Analysis bath temp.:"
        df.iat[12, start + 3] = "77.300 K"
        df.iat[14, start] = "Sample mass:"
        df.iat[14, start + 1] = "0.0815 g"

    df.iat[25, 0] = "概要报告"
    df.iat[31, 0] = "在p/p° = 0.291971689的单点表面积:"
    df.iat[31, 1] = "475.7198 m²/g"
    df.iat[33, 0] = "BET 表面积:"
    df.iat[33, 1] = "530.9603 m²/g"
    df.iat[41, 0] = "孔的单点脱附总孔容"
    df.iat[41, 1] = "1.427695 cm³/g"
    df.iat[53, 0] = "吸附平均孔径 (4V/A by BET):"
    df.iat[53, 1] = "107.556 Å"
    df.iat[55, 0] = "脱附平均孔径 (4V/A by BET):"
    df.iat[55, 1] = "107.556 Å"

    df.iat[25, 11] = "等温线线性图"
    df.iat[29, 11] = "相对压力(p/p°)"
    df.iat[29, 12] = "吸附量(cm3/g STP)"
    df.iat[29, 13] = "相对压力(p/p°)"
    df.iat[29, 14] = "吸附量(cm3/g STP)"
    df.iat[30, 11] = 0.0530187657
    df.iat[30, 12] = 71.45389756
    df.iat[30, 13] = 0.9889
    df.iat[30, 14] = 922.99
    df.iat[32, 11] = 0.0883
    df.iat[32, 12] = 86.33
    df.iat[32, 13] = 0.9794
    df.iat[32, 14] = 890.14

    df.iat[25, 63] = "BJH 吸附 积分孔体积 (较大)"
    df.iat[29, 63] = "孔 直径 (A)"
    df.iat[29, 64] = "孔体积(cm3/g)"
    df.iat[30, 63] = 481.1488
    df.iat[30, 64] = 0.830174
    df.iat[31, 63] = 254.1529
    df.iat[31, 64] = 0.922026

    df.iat[25, 68] = "BJH 吸附 dV/dD 孔体积"
    df.iat[29, 68] = "孔 直径 (A)"
    df.iat[29, 69] = "dV/dD 孔体积 (cm3/g·Å)"
    df.iat[30, 68] = 564.1852
    df.iat[30, 69] = 0.0006607
    df.iat[31, 68] = 300.9175
    df.iat[31, 69] = 0.0004046

    df.iat[25, 73] = "BJH 吸附 dV/dlog(D) 孔体积"
    df.iat[29, 73] = "孔 直径 (A)"
    df.iat[29, 74] = "dV/dlog(D) 孔体积(cm3/g)"
    df.iat[30, 73] = 564.1852
    df.iat[30, 74] = 1.488614

    df.iat[25, 85] = "BJH 脱附 积分孔体积 (较大)"
    df.iat[29, 85] = "孔 直径 (A)"
    df.iat[29, 86] = "孔体积(cm3/g)"
    df.iat[30, 85] = 951.18
    df.iat[30, 86] = 0.054234

    df.iat[25, 90] = "BJH 脱附 dV/dD 孔体积"
    df.iat[29, 90] = "孔 直径 (A)"
    df.iat[29, 91] = "dV/dD 孔体积 (cm3/g·Å)"
    df.iat[30, 90] = 1128.3025
    df.iat[30, 91] = 0.0000687

    df.iat[25, 95] = "BJH 脱附 dV/dlog(D) 孔体积"
    df.iat[29, 95] = "孔 直径 (A)"
    df.iat[29, 96] = "dV/dlog(D) 孔体积(cm3/g)"
    df.iat[30, 95] = 1128.3025
    df.iat[30, 96] = 0.206697

    with pd.ExcelWriter(path) as writer:
        df.to_excel(writer, index=False, header=False)


def test_detect_tristar_file_identifies_tristar_workbook(tmp_path: Path) -> None:
    path = tmp_path / "tristar.xlsx"
    _write_tristar_fixture(path)

    assert detect_tristar_file(path) is True


def test_detect_tristar_file_rejects_unrelated_workbook(tmp_path: Path) -> None:
    path = tmp_path / "other.xlsx"
    pd.DataFrame([["Other Instrument"]]).to_excel(path, index=False, header=False)

    assert detect_tristar_file(path) is False


def test_parse_tristar_file_extracts_isotherm_and_metadata(tmp_path: Path) -> None:
    path = tmp_path / "tristar.xlsx"
    _write_tristar_fixture(path)

    result = parse_tristar_file(path)

    assert result.sample_name == "PMSO"
    assert list(result.df.columns) == ["p_over_p0", "quantity_adsorbed", "branch"]
    assert result.df["branch"].tolist() == ["adsorption", "adsorption", "desorption", "desorption"]
    assert result.meta["instrument"] == "TriStar II Plus 3.03"
    assert result.meta["sample_mass_g"] == 0.0815
    assert result.meta["adsorbate"] == "N2"
    assert result.meta["bath_temp_K"] == 77.3
    assert result.meta["bet_surface_area_m2g"] == 530.9603
    assert result.meta["total_pore_volume_cm3g"] == 1.427695


def test_parse_tristar_file_tolerates_single_blank_rows_inside_isotherm(tmp_path: Path) -> None:
    path = tmp_path / "tristar.xlsx"
    _write_tristar_fixture(path)

    result = parse_tristar_file(path)

    assert len(result.df) == 4
    assert result.df["p_over_p0"].tolist() == [0.0530187657, 0.0883, 0.9889, 0.9794]


def test_parse_tristar_file_extracts_bjh_plot_tables(tmp_path: Path) -> None:
    path = tmp_path / "tristar.xlsx"
    _write_tristar_fixture(path)

    result = parse_tristar_file(path)

    expected_tables = {
        "bjh_adsorption_cumulative_pore_volume",
        "bjh_adsorption_dv_dD",
        "bjh_adsorption_dv_dlogD",
        "bjh_desorption_cumulative_pore_volume",
        "bjh_desorption_dv_dD",
        "bjh_desorption_dv_dlogD",
    }
    assert expected_tables.issubset(result.extra_tables.keys())
    assert result.extra_tables["bjh_adsorption_dv_dD"].to_dict(orient="records") == [
        {"pore_diameter_A": 564.1852, "dV_dD_pore_volume_cm3_g_A": 0.0006607},
        {"pore_diameter_A": 300.9175, "dV_dD_pore_volume_cm3_g_A": 0.0004046},
    ]
    assert result.extra_tables["bjh_desorption_dv_dlogD"].to_dict(orient="records") == [
        {"pore_diameter_A": 1128.3025, "dV_dlogD_pore_volume_cm3_g": 0.206697},
    ]


def test_parse_tristar_file_raises_controlled_error_for_missing_isotherm(tmp_path: Path) -> None:
    path = tmp_path / "tristar.xlsx"
    _write_tristar_fixture(path)
    df = pd.read_excel(path, header=None)
    df.iat[25, 11] = "Other Section"
    with pd.ExcelWriter(path) as writer:
        df.to_excel(writer, index=False, header=False)

    with pytest.raises(ValueError, match="isotherm"):
        parse_tristar_file(path)
