from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Protocol
import pandas as pd


@dataclass
class ImportResult:
    df: pd.DataFrame
    sample_name: str
    meta: Dict[str, Any] = field(default_factory=dict)
    extra_tables: Dict[str, pd.DataFrame] = field(default_factory=dict)


class SampleProtocol(Protocol):
    """插件看到的 sample 接口，隔离内部实现。"""
    active_data: pd.DataFrame
    processed_data: pd.DataFrame | None


class OperationContext:
    """操作上下文，封装对 sample 的访问。插件通过 ctx 操作数据，不直接访问 SampleRecord。"""

    def __init__(self, sample: SampleProtocol):
        self._sample = sample

    @property
    def data(self) -> pd.DataFrame:
        """获取当前活动数据（copy）"""
        return self._sample.active_data.copy()

    def update(self, df: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
        """更新处理后的数据"""
        self._sample.processed_data = df
        return True, {"status": "updated", "rows": len(df)}

    def compute(self, result: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """仅返回计算结果，不修改数据（如积分面积）"""
        return False, result
