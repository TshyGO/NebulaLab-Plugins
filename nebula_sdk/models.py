from typing import Any

from .types import SampleProtocol, OperationContext

OperationResult = tuple[bool, dict[str, Any]]

__all__ = ["SampleProtocol", "OperationContext", "OperationResult"]
