# NebulaLab 插件开发入门指南

欢迎使用 NebulaLab 插件开发系统！本文档将引导你完成从环境搭建到开发第一个插件的全过程。

## 开发环境准备

在开始编写插件前，请确保您的开发环境满足以下要求：

- **Python**: 3.10 或以上版本
- **Pandas**: NebulaLab 底层依赖 Pandas 进行数据处理
- **Nebula SDK**: 这是 NebulaLab 提供的标准开发包，包含了所有你需要与应用交互的接口

Nebula SDK 随 NebulaLab 应用一同分发，无需单独安装。在开发时，你可以通过下方代码中展示的 `_ensure_nebula_sdk_importable()` 方式自动定位 SDK，使其在本地开发环境和安装到应用内时都能正常导入。

## 插件基本结构

一个标准的 NebulaLab 插件应至少包含以下内容：

```
my_awesome_plugin/
├── __init__.py         # 插件主入口，定义数据处理逻辑
└── plugin.json         # 插件清单，声明版本、依赖及配置
```

如果插件需要提供自定义的用户界面（UI），还可以添加 `panel.html`：

```
my_awesome_plugin/
├── __init__.py
├── plugin.json
└── panel.html          # (可选) 自定义配置面板
```

## `plugin.json` 清单文件

`plugin.json` 用于向 NebulaLab 声明你的插件属性。以下是一个典型的配置示例：

```json
{
  "id": "my-awesome-plugin",
  "name": "我的数据处理插件",
  "version": "1.0.0",
  "author": "您的名字",
  "description": "这是我的第一个 NebulaLab 插件",
  "category": "preprocessing",
  "min_app_version": "0.6.0",
  "operations": ["my_operation"],
  "enabled": true
}
```

*说明：*
- **`id`**: 只允许小写字母、数字、连字符和下划线。
- **`operations`**: 这是你在 `__init__.py` 中通过 `@op` 装饰器注册的函数名（操作名）。
- **`category`**: 插件的分类，常见的有 `preprocessing`（预处理）, `analysis`（分析）, `export`（导出）等。

如果你要做面板型插件，还可以继续补充：

```json
{
  "panel": "panel.html",
  "panel_title": "My Panel",
  "panel_icon": "chart",
  "panel_views": ["prep", "plots"],
  "panel_position": "right"
}
```

## 核心 SDK 概念

Nebula SDK 提供了两个非常重要的对象来编写插件：

1. **`@op` 装饰器**: 用于标记一个函数为可被 NebulaLab 调用的数据处理操作。它允许你定义需要在前端 UI 渲染的参数表单。
2. **`OperationContext` (ctx)**: 操作上下文。这是您的函数用来安全读取和更新表格数据的代理对象。

## 编写插件代码 (`__init__.py`)

现在，让我们编写一个简单的插件。它的功能是将用户指定的一列数据乘以一个固定的倍数，并将结果写入一个新列。

### 1. 引入必要的包

```python
from __future__ import annotations

from typing import Any, Dict
import pandas as pd

from nebula_sdk import OperationContext, op
```

> **说明：** `nebula_sdk` 由应用在加载插件时自动注入运行环境，直接 `import` 即可，无需手动设置路径。

### 2. 定义操作逻辑

使用 `@op` 装饰器定义你的操作函数，并在 `params_schema` 中声明需要的参数，系统会自动在前端生成对应的输入控件。

```python
@op(
    name="my_operation",
    display_name="倍数缩放",
    category="preprocessing",
    params_schema={
        "target_column": {
            "type": "column",        # 渲染为一个下拉框，让用户选择列
            "required": True,
            "label": "目标列",
        },
        "scale_factor": {
            "type": "float",         # 渲染为一个数字输入框
            "required": False,
            "default": 1.5,
            "label": "缩放倍数",
        },
        "output_column": {
            "type": "str",           # 渲染为一个文本输入框
            "required": False,
            "default": "scaled_result",
            "label": "输出列名",
        },
    },
    description="读取数据列，将其乘以指定倍数，并保存到新列中。",
)
def my_operation(sample, params: Dict[str, Any]):
    """
    主要的处理函数。
    sample: 当前数据集的包装对象。
    params: 用户在前端界面填写的参数值。
    """
    
    # 1. 包装数据上下文
    ctx = OperationContext(sample)
    df = ctx.data  # 获取当前数据的副本，类型为 pandas.DataFrame
    
    # 2. 读取前端传入的参数
    target_column = params.get("target_column")
    scale_factor = float(params.get("scale_factor", 1.5))
    output_column = params.get("output_column", "scaled_result")
    
    # 3. 参数校验
    if not target_column:
        raise ValueError("请指定需要处理的目标列")
        
    if target_column not in df.columns:
        raise ValueError(f"数据中找不到列 '{target_column}'")
        
    # 4. 执行数据处理逻辑
    try:
        # 在副本上进行操作：将目标列乘以缩放因子，存入新列
        df[output_column] = df[target_column] * scale_factor
        
        # 5. 更新数据并返回状态
        # ctx.update() 表示数据发生了变更，并通知系统更新表格
        return ctx.update(df)
        
    except Exception as e:
        # 处理可能的异常并抛出错误信息
        raise RuntimeError(f"数据处理失败: {str(e)}")
```

## 测试插件

在完成开发后，您可以通过以下方式在本地测试插件：

1. 将你的插件文件夹（例如 `my_awesome_plugin/`）复制到 NebulaLab 应用程序的 `plugins/` 目录下。
2. 启动 NebulaLab。
3. 系统会自动扫描 `plugins/` 目录并在工作流中加载该插件。您可以在工作流的相应分类中找到 `倍数缩放` 操作，并进行测试。

## 提交到插件市场

一旦您确认插件可以完美工作，即可将其提交到插件市场分享给所有用户。具体提交流程，请参考 [贡献指南](./contributing.md)。
