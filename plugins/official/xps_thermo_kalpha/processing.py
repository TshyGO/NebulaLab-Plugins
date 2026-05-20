from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from .compat import OperationContext, op


def _require_numeric_column(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        raise ValueError(f"Unknown column: {column}")
    values = pd.to_numeric(df[column], errors="coerce")
    if values.isna().all():
        raise ValueError(f"Column '{column}' does not contain numeric values")
    return values


@op(
    name="xps_normalize_intensity",
    display_name="XPS 强度归一化",
    category="xps",
    params_schema={
        "intensity_column": {"type": "column", "required": False, "default": "intensity_cps", "label": "强度列"},
        "energy_column": {"type": "column", "required": False, "default": "binding_energy_eV", "label": "结合能列"},
        "method": {"type": "select", "required": False, "default": "max", "options": ["max", "area", "min-max"], "label": "方法"},
        "output_column": {"type": "string", "required": False, "default": "intensity_normalized", "label": "输出列"},
    },
    description="对 Thermo K-Alpha XPS 谱图强度进行最大值、面积或 min-max 归一化。",
)
def xps_normalize_intensity(sample, params: Dict[str, Any]):
    ctx = OperationContext(sample)
    df = ctx.data
    intensity_column = str(params.get("intensity_column") or "intensity_cps")
    energy_column = str(params.get("energy_column") or "binding_energy_eV")
    method = str(params.get("method") or "max").lower()
    output_column = str(params.get("output_column") or "intensity_normalized")

    y = _require_numeric_column(df, intensity_column)
    if method == "max":
        denom = y.max()
    elif method == "min-max":
        denom = y.max() - y.min()
        y = y - y.min()
    elif method == "area":
        x = _require_numeric_column(df, energy_column)
        ordered = pd.DataFrame({"x": x, "y": y}).dropna().sort_values("x")
        denom = float(abs((ordered["y"].shift(-1) + ordered["y"])[:-1].mul((ordered["x"].shift(-1) - ordered["x"])[:-1]).sum() / 2.0))
    else:
        raise ValueError("method must be one of: max, area, min-max")

    if denom == 0 or pd.isna(denom):
        raise ValueError("Cannot normalize with a zero or NaN denominator")

    result = df.copy()
    result[output_column] = y / denom
    updated, info = ctx.update(result)
    info.update({"operation": "xps_normalize_intensity", "method": method, "output_column": output_column})
    return updated, info


@op(
    name="xps_calibrate_binding_energy",
    display_name="XPS 结合能校准",
    category="xps",
    params_schema={
        "energy_column": {"type": "column", "required": False, "default": "binding_energy_eV", "label": "结合能列"},
        "intensity_column": {"type": "column", "required": False, "default": "intensity_cps", "label": "强度列"},
        "reference_peak_eV": {"type": "float", "required": False, "default": 284.8, "label": "参考峰 eV"},
        "observed_peak_eV": {"type": "float", "required": False, "label": "观测峰 eV；为空时使用最大强度点"},
        "output_column": {"type": "string", "required": False, "default": "binding_energy_calibrated_eV", "label": "输出列"},
    },
    description="按参考峰位置平移校准 XPS 结合能轴，默认参考 C 1s = 284.8 eV。",
)
def xps_calibrate_binding_energy(sample, params: Dict[str, Any]):
    ctx = OperationContext(sample)
    df = ctx.data
    energy_column = str(params.get("energy_column") or "binding_energy_eV")
    intensity_column = str(params.get("intensity_column") or "intensity_cps")
    reference_peak = float(params.get("reference_peak_eV") or 284.8)
    output_column = str(params.get("output_column") or "binding_energy_calibrated_eV")

    energy = _require_numeric_column(df, energy_column)
    observed_param = params.get("observed_peak_eV")
    if observed_param in (None, ""):
        intensity = _require_numeric_column(df, intensity_column)
        observed_peak = float(energy.loc[intensity.idxmax()])
    else:
        observed_peak = float(observed_param)

    shift = reference_peak - observed_peak
    result = df.copy()
    result[output_column] = energy + shift
    updated, info = ctx.update(result)
    info.update(
        {
            "operation": "xps_calibrate_binding_energy",
            "reference_peak_eV": reference_peak,
            "observed_peak_eV": observed_peak,
            "shift_eV": shift,
            "output_column": output_column,
        }
    )
    return updated, info