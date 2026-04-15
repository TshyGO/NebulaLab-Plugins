# 贡献指南

感谢您有兴趣为 NebulaLab 插件市场贡献力量！通过向市场提交插件，您的代码可以帮助全球的科研人员和数据分析师更高效地工作。

本文档将指导您如何向 NebulaLab 插件官方仓库提交您的插件。

## 提交前准备

在提交您的插件之前，请确保完成以下检查：

1. **功能完整且无 Bug**: 在本地或 NebulaLab 客户端中进行充分测试，确保它能在给定的输入数据下正确执行并返回期望结果。
2. **完整的 Metadata (`plugin.json`)**:
   - `id`: 插件唯一标识符（例如 `yourname-awesome-plugin`）。
   - `name`: 插件显示名称。
   - `version`: 语义化版本号（例如 `1.0.0`）。
   - `author`: 您的名字或组织名。
   - `description`: 清晰描述插件的用途和功能。
   - `operations`: 准确列出在 `__init__.py` 中注册的操作函数名。
   - `category`: 为插件选择合适的分类。
3. **干净的代码结构**: 不包含与插件运行无关的文件（如本地测试数据、缓存文件 `__pycache__` 等）。
4. **代码规范**: Python 代码推荐遵循 PEP 8 规范，并且包含必要的注释和说明。

## 提交流程

所有官方社区插件都托管在我们的 GitHub 仓库中：[TshyGO/NebulaLab-Plugins](https://github.com/TshyGO/NebulaLab-Plugins)。

请遵循以下标准的 GitHub Pull Request 流程来提交您的插件：

### 1. Fork 并克隆仓库

首先，Fork 官方仓库到您的 GitHub 账户，然后将其克隆到本地：

```bash
git clone https://github.com/您的用户名/NebulaLab-Plugins.git
cd NebulaLab-Plugins
```

### 2. 创建您的分支

基于 `main` 分支创建一个新的分支用于提交插件：

```bash
git checkout -b feature/add-my-awesome-plugin
```

### 3. 添加您的插件文件

将您开发好的插件文件夹完整地复制到 `plugins/` 目录下。

```bash
cp -r /path/to/your/plugin plugins/my-awesome-plugin/
```

确保目录结构类似如下：
```
NebulaLab-Plugins/
└── plugins/
    └── my-awesome-plugin/
        ├── __init__.py
        ├── plugin.json
        └── (其他文件，例如 panel.html)
```

### 4. 更新插件索引表 (可选)

*(通常维护者会在合并 PR 时更新索引，但如果方便，您也可以自己更新。)*

打开 `NebulaLab-Plugins/plugins-index.json`，在数组中添加您的插件条目（与您的 `plugin.json` 保持一致），例如：

```json
{
  "id": "my-awesome-plugin",
  "name": "我的数据处理插件",
  "version": "1.0.0",
  "author": "您的名字",
  "source": "community",
  "description": "这是我的第一个 NebulaLab 插件",
  "category": "preprocessing",
  "min_app_version": "0.6.0",
  "download_url": "https://github.com/TshyGO/NebulaLab-Plugins/releases/download/plugins/my-awesome-plugin-1.0.0.zip"
}
```

### 5. 提交并推送

将您的更改提交并推送到您的远程 Fork 仓库：

```bash
git add plugins/my-awesome-plugin/
git commit -m "feat(plugin): 添加 my-awesome-plugin 插件"
git push origin feature/add-my-awesome-plugin
```

### 6. 创建 Pull Request

回到官方仓库页面，点击 "New Pull Request"。在描述中清晰地说明您的插件功能、适用场景以及依赖的最低版本。

## 审核标准

维护者将基于以下标准审核您的 Pull Request：

- **安全性**: 插件不应包含恶意代码，不能随意访问文件系统或网络（除非有明确说明及合理需求）。
- **稳定性**: 对异常数据和错误参数有适当的容错和提示机制。
- **性能**: 不会在处理常见规模数据时造成应用卡死。
- **UI/UX**: 在 `params_schema` 中定义了对用户友好的界面参数。

通过审核后，您的插件将会被合并，并在 NebulaLab 客户端的“插件市场”中向所有用户展示！

## 疑问与支持

如果您在开发或提交过程中遇到任何问题，欢迎通过以下方式寻求帮助：

- 在官方仓库提交 [Issue](https://github.com/TshyGO/NebulaLab-Plugins/issues)
- 查阅 [入门指南](./getting_started.md) 获取更多开发细节

期待您的精彩贡献！