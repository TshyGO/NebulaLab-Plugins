from __future__ import annotations
from typing import Any, Callable, Dict

# 用于收集注册在独立 SDK 环境的元数据（主要用于文档生成和独立测试）。
# 当该插件在 Nebula Lab 主程序运行时，这里的 _registry 会被主程序的注册器所替代。
_registry: Dict[str, Dict[str, Any]] = {}
_importer_registry: Dict[str, Dict[str, Any]] = {}

def register_operation(
    name: str,
    display_name: str = None,
    category: str = "custom",
    params_schema: Dict[str, Any] = None,
    description: str = None,
):
    """
    SDK 版插件操作注册装饰器。

    在开发阶段：它会将配置注入模块的 _registry。
    在生产运行阶段：当 Nebula Lab 加载插件时，主程序会接管这个装饰器，使操作能在平台内正常执行。

    函数签名必须为：
        def handler(sample: SampleProtocol, params: dict) -> Tuple[bool, dict]
        或者
        def handler(ctx: OperationContext, params: dict) -> Tuple[bool, dict]
        （为了与主程序完全兼容，请依照平台规范编写 handler）
    """
    def decorator(func: Callable) -> Callable:
        metadata = {
            "name": name,
            "display_name": display_name or name,
            "category": category,
            "params_schema": params_schema or {},
            "description": description or "",
            "handler": func
        }
        _registry[name] = metadata
        return func

    return decorator

# 提供两个常用别名，兼容 engine.plugins.decorators 的习惯
op = register_operation
register_operation_decorator = register_operation


def _normalize_extensions(extensions):
    normalized = []
    for item in extensions or []:
        ext = str(item).strip().lower()
        if not ext:
            continue
        if not ext.startswith("."):
            ext = f".{ext}"
        if ext not in normalized:
            normalized.append(ext)
    return normalized


def register_importer(
    id: str,
    name: str,
    extensions,
    description: str = None,
    category: str = "custom",
    min_app_version: str = None,
    detect_fn: Callable | None = None,
):
    def decorator(func: Callable) -> Callable:
        metadata = {
            "id": id,
            "name": name,
            "extensions": _normalize_extensions(extensions),
            "description": description or "",
            "category": category,
            "min_app_version": min_app_version,
            "handler": func,
            "detect_fn": detect_fn,
        }
        _importer_registry[id] = metadata
        return func

    return decorator


importer = register_importer
