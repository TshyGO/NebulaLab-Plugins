from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

import pandas as pd


def _ensure_nebula_sdk_importable() -> None:
    """
    Make `nebula_sdk` importable in two common cases:
    1. You are developing inside this repository.
    2. The plugin folder has been copied into the app's `plugins/` directory,
       where a bundled `nebula_sdk.py` or `nebula_sdk/` is already available.
    """

    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "nebula_sdk").is_dir() or (parent / "nebula_sdk.py").is_file():
            parent_str = str(parent)
            if parent_str not in sys.path:
                sys.path.insert(0, parent_str)
            return


_ensure_nebula_sdk_importable()

# Import the SDK objects you will use most often:
# - `op`: decorator for declaring an operation
# - `OperationContext`: helper for reading current data and writing results back
from nebula_sdk import OperationContext, op


@op(
    name="my_operation",
    display_name="我的插件操作",
    category="preprocessing",
    params_schema={
        # `column`: renders a column picker in the app UI.
        "y_column": {
            "type": "column",
            "required": True,
            "label": "Y 列 / Y Column",
        },
        # `int`: renders an integer input.
        "window_size": {
            "type": "int",
            "required": False,
            "default": 5,
            "label": "窗口大小 / Window Size",
        },
        # `float`: renders a floating-point input.
        "scale": {
            "type": "float",
            "required": False,
            "default": 1.0,
            "label": "缩放系数 / Scale",
        },
        # `str`: renders a text input.
        "output_column": {
            "type": "str",
            "required": False,
            "default": "my_result",
            "label": "输出列名 / Output Column",
        },
    },
    description="示例模板：读取数据、处理数据，并把结果写回表格。",
)
def my_operation(sample, params: Dict[str, Any]):
    """
    Main plugin entry point.

    The app will call this function with:
    - `sample`: the current dataset wrapper
    - `params`: values collected from the form described by `params_schema`
    """

    ctx = OperationContext(sample)
    df = ctx.data

    try:
        # Read parameters and validate them explicitly.
        y_column = params.get("y_column")
        if not y_column:
            raise ValueError("Missing required parameter: y_column")
        if y_column not in df.columns:
            raise ValueError(f"Unknown column: {y_column}")

        window_size = int(params.get("window_size", 5))
        scale = float(params.get("scale", 1.0))
        output_column = str(params.get("output_column", "my_result")).strip() or "my_result"

        if window_size <= 0:
            raise ValueError("window_size must be greater than 0")

        # Convert the selected column to numeric data.
        values = pd.to_numeric(df[y_column], errors="coerce")
        if values.isna().any():
            raise ValueError(f"Column '{y_column}' contains non-numeric or missing values")

        result = df.copy()

        # Example data modification:
        # here we compute a rolling mean and then apply a scale factor.
        result[output_column] = values.rolling(window=window_size, min_periods=1).mean() * scale

        # `ctx.update(...)` means "this operation changed the dataset".
        updated, info = ctx.update(result)
        info.update(
            {
                "operation": "my_operation",
                "source_column": y_column,
                "output_column": output_column,
                "window_size": window_size,
                "scale": scale,
            }
        )
        return updated, info

    except Exception as exc:
        # Error handling pattern:
        # raise a clear ValueError so the host app can surface a readable message.
        raise ValueError(f"my_operation failed: {exc}") from exc


# Compute-only mode example:
# If you want to return a metric without modifying the table, use `ctx.compute(...)`.
#
# def summarize_signal(sample, params: Dict[str, Any]):
#     ctx = OperationContext(sample)
#     df = ctx.data
#     y_column = params["y_column"]
#     values = pd.to_numeric(df[y_column], errors="coerce").dropna()
#     return ctx.compute(
#         {
#             "operation": "summarize_signal",
#             "mean": float(values.mean()),
#             "max": float(values.max()),
#         }
#     )
