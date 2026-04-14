# Plugin Template / 插件模板说明

Use this folder as the starting point for a new NebulaGraph plugin.

把这个目录作为你开发 NebulaGraph 插件的起点模板。

## 3 Steps / 三步开始

1. Edit `plugin.json`

Set your plugin ID, name, author, description, and operation names.

先修改 `plugin.json`，填写插件 ID、名称、作者、描述和操作名。

2. Edit `__init__.py`

Replace the sample logic with your real algorithm, and update the `@op(...)` metadata plus parameter schema.

再修改 `__init__.py`，把示例逻辑替换为你的真实算法，并更新 `@op(...)` 元数据和参数 schema。

3. Test inside the app

Copy the whole plugin folder into the application's `plugins/` directory, restart the app, and verify your operation appears in `Plugin Operations`.

最后把整个插件目录放进应用的 `plugins/` 目录，重启应用，并确认你的操作出现在 `Plugin Operations` 面板里。
