---
name: nebula-plugin-dev
description: 为 NebulaLab 开发插件的完整指南，包含操作型和面板型插件的模板、字段说明和限制。
---

# NebulaLab 插件开发

## 插件类型

- **操作型（Operations）**：在数据处理面板的"插件操作"下拉中出现，用户选择参数后执行，修改数据集
- **面板型（Panel）**：在顶栏出现图标，点击后在指定位置弹出 HTML 面板
- **组合型**：同时有操作和面板

## 目录结构

```
my-plugin/
  plugin.json       # 必须
  __init__.py       # 有操作时必须
  panel.html        # 有面板时必须（文件名在 plugin.json 里指定）
  requirements.txt  # 可选，列出 pip 依赖
```

单文件插件（只有 `__init__.py`，无 `plugin.json`）仅支持操作，不支持面板和启用/禁用。建议始终使用目录结构。

## plugin.json 完整字段

```json
{
  "id": "my-plugin",           // 必须，唯一 ID，只允许字母/数字/连字符/下划线
  "name": "My Plugin",         // 显示名称
  "version": "1.0.0",
  "description": "插件描述",
  "enabled": true,
  "min_app_version": "0.7.0",  // 可选
  "max_app_version": "1.0.0",  // 可选
  "dependencies": ["scipy", "numpy"],  // pip 包名列表，启动时检测是否安装

  // 操作型插件字段
  "operations": ["my_operation"],  // __init__.py 里注册的操作名列表（必须与 @op(name=) 一致）
  "category": "custom",            // 操作分类
  "params_schema": {},             // 操作级别的默认 schema（会被 @op 里的 params_schema 覆盖）

  // 面板型插件字段
  "panel": "panel.html",           // 面板 HTML 文件名
  "panel_title": "My Panel",       // 面板标题栏显示的名字
  "panel_position": "right",       // 面板位置：left / right / bottom / center / floating
  "panel_views": ["prep", "plots", "export"],  // 在哪些 tab 里显示图标
  "allow_ai": false                // 是否允许面板调用外部 AI API（默认 false）
}
```

**关键约束**：`operations` 列表中的名称必须与 `__init__.py` 中 `@op(name="...")` 的 `name` 参数完全一致。

## 操作型插件模板（__init__.py）

```python
from __future__ import annotations
from typing import Any, Dict
import pandas as pd

from nebula_sdk import OperationContext, op

@op(
    name="my_operation",           # 必须与 plugin.json 中 operations 列表一致
    display_name="My Operation",
    category="custom",
    description="做一些数据处理",
    params_schema={
        "column": {
            "type": "column",      # column / str / int / float
            "label": "目标列",
            "required": True
        },
        "factor": {
            "type": "float",
            "label": "系数",
            "default": 1.0
        }
    }
)
def my_operation(sample, params: Dict[str, Any]):
    ctx = OperationContext(sample)
    df = ctx.data                  # 获取当前数据的防御性拷贝（pd.DataFrame）
    col = params["column"]
    df[col] = df[col] * params.get("factor", 1.0)
    return ctx.update(df)          # 修改数据：返回 (True, {"status": "updated", "rows": N})
    # 只计算不修改：return ctx.compute({"result": 42})  返回 (False, {...})
```

**params_schema 类型**：
- `column`：列选择器
- `str`：文本输入
- `int`：整数输入
- `float`：浮点数输入

**OperationContext API**：
- `ctx.data` -> `pd.DataFrame`：获取当前数据的拷贝
- `ctx.update(df)` -> `(True, {...})`：更新数据，表示数据已修改
- `ctx.compute(result_dict)` -> `(False, {...})`：仅返回计算结果，不修改数据

**沙箱限制**：插件在 subprocess 沙箱中执行，无法访问宿主进程内存，无法 import 宿主内部模块（`engine.*`）。标准库和已安装的 pip 包可以正常使用。

## 面板型插件模板（panel.html）

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: sans-serif; padding: 16px; }
  </style>
</head>
<body>
  <button onclick="refreshData()">刷新数据</button>
  <button onclick="closePanel()">关闭</button>

  <script>
    // 刷新宿主的数据视图
    function refreshData() {
      window.parent.postMessage({ type: 'nebula:refresh-data' }, '*')
    }

    // 关闭面板
    function closePanel() {
      window.parent.postMessage({ type: 'nebula:close-panel' }, '*')
    }
  </script>
</body>
</html>
```

**postMessage 类型**（type 必须以 `nebula:` 开头）：
- `nebula:refresh-data`：刷新当前 session 的数据查询缓存
- `nebula:close-panel`：关闭面板

**allow_ai 说明**：
- `allow_ai: false`（默认）：面板完全无法发出外部网络请求
- `allow_ai: true`：面板可以 fetch 调用 OpenAI / Anthropic / DeepSeek 等 AI API（域名白名单由应用维护）

## 打包发布

```bash
cd my-plugin/
zip -r my-plugin-1.0.0.zip .
```

zip 根目录直接包含插件文件（解压后得到 `plugin.json`、`__init__.py` 等），或 zip 里包一层同名目录也可以。用户在插件管理界面点"从本地安装"选择 zip 文件。