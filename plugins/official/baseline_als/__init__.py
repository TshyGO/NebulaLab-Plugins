from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.sparse.linalg import spsolve


def _ensure_nebula_sdk_importable() -> None:
    """Support both repo-local development and app-side plugin loading."""

    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "nebula_sdk").is_dir() or (parent / "nebula_sdk.py").is_file():
            parent_str = str(parent)
            if parent_str not in sys.path:
                sys.path.insert(0, parent_str)
            return


_ensure_nebula_sdk_importable()

from nebula_sdk import OperationContext, op


def _baseline_als(y: np.ndarray, lam: float, p: float, niter: int) -> np.ndarray:
    """Estimate the baseline with asymmetric least squares smoothing."""

    length = y.shape[0]
    if length < 3:
        raise ValueError("ALS baseline correction requires at least 3 data points")

    diff_matrix = sparse.diags([1.0, -2.0, 1.0], [0, 1, 2], shape=(length - 2, length), format="csc")
    penalty = lam * (diff_matrix.T @ diff_matrix)
    weights = np.ones(length, dtype=float)

    for _ in range(niter):
        weight_matrix = sparse.diags(weights, offsets=0, shape=(length, length), format="csc")
        baseline = spsolve(weight_matrix + penalty, weights * y)
        weights = p * (y > baseline) + (1.0 - p) * (y < baseline)

    return np.asarray(baseline, dtype=float)


@op(
    name="baseline_als",
    display_name="ALS 基线校正",
    category="preprocessing",
    params_schema={
        "y_column": {
            "type": "column",
            "required": True,
            "label": "Y 列 / Y Column",
        },
        "lam": {
            "type": "float",
            "required": False,
            "default": 1e5,
            "label": "平滑参数 λ / Lambda",
        },
        "p": {
            "type": "float",
            "required": False,
            "default": 0.01,
            "label": "不对称参数 p / Asymmetry",
        },
        "niter": {
            "type": "int",
            "required": False,
            "default": 10,
            "label": "迭代次数 / Iterations",
        },
    },
    description="使用非对称最小二乘法（ALS）估计基线，并将校正后的结果写回数据表。",
)
def baseline_als(sample, params: Dict[str, Any]):
    """A complete reference plugin that performs ALS baseline correction."""

    ctx = OperationContext(sample)
    df = ctx.data

    y_column = params.get("y_column")
    if not y_column:
        raise ValueError("Missing required parameter: y_column")
    if y_column not in df.columns:
        raise ValueError(f"Unknown column: {y_column}")

    lam = float(params.get("lam", 1e5))
    p = float(params.get("p", 0.01))
    niter = int(params.get("niter", 10))

    if lam <= 0:
        raise ValueError("lam must be greater than 0")
    if not 0 < p < 1:
        raise ValueError("p must be between 0 and 1")
    if niter <= 0:
        raise ValueError("niter must be greater than 0")

    y_values = pd.to_numeric(df[y_column], errors="coerce")
    if y_values.isna().any():
        raise ValueError(f"Column '{y_column}' contains non-numeric or missing values")

    signal = y_values.to_numpy(dtype=float)
    baseline = _baseline_als(signal, lam=lam, p=p, niter=niter)

    result = df.copy()
    baseline_column = f"{y_column}_baseline"
    result[y_column] = signal - baseline
    result[baseline_column] = baseline

    updated, info = ctx.update(result)
    info.update(
        {
            "operation": "baseline_als",
            "updated_column": y_column,
            "baseline_column": baseline_column,
            "lam": lam,
            "p": p,
            "niter": niter,
        }
    )
    return updated, info
