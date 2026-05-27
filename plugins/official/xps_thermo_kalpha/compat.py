from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict

import pandas as pd


def _ensure_nebula_sdk_importable() -> None:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "nebula_sdk").is_dir() or (parent / "nebula_sdk.py").is_file():
            parent_str = str(parent)
            if parent_str not in sys.path:
                sys.path.insert(0, parent_str)
            return


@dataclass
class ImportResult:
    df: pd.DataFrame
    sample_name: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)
    extra_tables: Dict[str, pd.DataFrame] = field(default_factory=dict)


class OperationContext:
    def __init__(self, sample: Any):
        self.sample = sample

    @property
    def data(self) -> pd.DataFrame:
        return getattr(self.sample, "active_data")

    def update(self, df: pd.DataFrame) -> tuple[bool, dict[str, Any]]:
        self.sample.processed_data = df
        return True, {"rows": int(len(df)), "columns": list(df.columns)}


def register_importer(
    id: str,
    name: str,
    extensions: list[str] | tuple[str, ...],
    description: str | None = None,
    category: str = "custom",
    min_app_version: str | None = None,
    detect_fn: Callable[[Path], bool] | None = None,
    priority: int = 0,
) -> Callable[[Callable[[str | Path], ImportResult]], Callable[[str | Path], ImportResult]]:
    """Register an importer in both app sandbox and repo-local SDK environments."""

    try:
        from engine.plugins.importers import register_importer as engine_register_importer
    except ImportError:
        engine_register_importer = None

    if engine_register_importer is not None:
        metadata = {
            "name": name,
            "extensions": list(extensions),
            "description": description or "",
            "category": category,
            "min_app_version": min_app_version,
            "priority": priority,
        }

        def decorator(func: Callable[[str | Path], ImportResult]) -> Callable[[str | Path], ImportResult]:
            engine_register_importer(id, func, metadata, detect_fn=detect_fn, source="user")
            return func

        return decorator

    try:
        _ensure_nebula_sdk_importable()
        from nebula_sdk import register_importer as sdk_register_importer
    except ImportError:
        def decorator(func: Callable[[str | Path], ImportResult]) -> Callable[[str | Path], ImportResult]:
            return func

        return decorator

    return sdk_register_importer(
        id=id,
        name=name,
        extensions=extensions,
        description=description,
        category=category,
        min_app_version=min_app_version,
        detect_fn=detect_fn,
        priority=priority,
    )


def op(
    name: str,
    display_name: str | None = None,
    category: str = "custom",
    params_schema: Dict[str, Any] | None = None,
    description: str | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register an operation in both app sandbox and repo-local SDK environments."""

    try:
        from engine.core.session_ops import register_operation as engine_register_operation
    except ImportError:
        engine_register_operation = None

    if engine_register_operation is not None:
        metadata = {
            "name": name,
            "display_name": display_name or name,
            "category": category,
            "params_schema": params_schema or {},
            "description": description or "",
        }

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            engine_register_operation(name, func, metadata, source="user")
            return func

        return decorator

    try:
        _ensure_nebula_sdk_importable()
        from nebula_sdk import op as sdk_op
    except ImportError:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            return func

        return decorator

    return sdk_op(
        name=name,
        display_name=display_name,
        category=category,
        params_schema=params_schema,
        description=description,
    )