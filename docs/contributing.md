# 贡献指南

感谢您有兴趣为 NebulaLab 插件市场贡献力量！社区插件采用**去中心化**模式——您的插件代码托管在自己的仓库中，只需向本仓库提交一条索引记录，审核通过后即可在所有用户的插件市场中展示。

## 提交前准备

在提交之前，请确保完成以下检查：

1. **功能完整且无 Bug**: 在本地或 NebulaLab 客户端中充分测试，确保插件在正常和异常输入下都能正确运行。
2. **完整的 `plugin.json`**:
   - `id`: 全局唯一标识符，只允许小写字母、数字和连字符（例如 `yourname-awesome-plugin`）。
   - `name`: 插件显示名称。
   - `version`: 语义化版本号（例如 `1.0.0`）。
   - `author`: 您的名字或组织名。
   - `description`: 清晰描述插件的用途和功能。
   - `operations`: 准确列出在 `__init__.py` 中注册的操作函数名。
   - `category`: 为插件选择合适的分类（如 `preprocessing`、`analysis`、`export`）。
3. **干净的打包内容**: zip 文件中不应包含 `__pycache__`、`.pyc`、本地测试数据等无关文件。
4. **代码规范**: Python 代码推荐遵循 PEP 8，并包含必要的注释。

## 提交流程

### 1. 在自己的仓库发布插件 Release

在您自己的 GitHub 仓库中，将插件打包为 zip 文件并发布 Release。zip 内应包含一个以插件 id 命名的文件夹：

```
my-awesome-plugin-1.0.0.zip
└── my-awesome-plugin/
    ├── __init__.py
    ├── plugin.json
    └── (其他文件，例如 panel.html)
```

打包示例：

```bash
# 在插件目录的上层运行
zip -r my-awesome-plugin-1.0.0.zip my-awesome-plugin/ --exclude "**/__pycache__/*" --exclude "**/*.pyc"
```

### 2. 计算 sha256

社区插件必须提供 zip 文件的 sha256 校验值，用于安装时的完整性验证：

```bash
# macOS / Linux
shasum -a 256 my-awesome-plugin-1.0.0.zip

# Windows PowerShell
Get-FileHash my-awesome-plugin-1.0.0.zip -Algorithm SHA256
```

记录输出的哈希值（全小写）。

### 3. Fork 本仓库并创建分支

```bash
git clone https://github.com/您的用户名/NebulaLab-Plugins.git
cd NebulaLab-Plugins
git checkout -b add-my-awesome-plugin
```

### 4. 在 `plugins-index.json` 添加您的插件条目

打开根目录下的 `plugins-index.json`，在 `plugins` 数组末尾添加一条记录：

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
  "download_url": "https://github.com/您的用户名/my-awesome-plugin/releases/download/v1.0.0/my-awesome-plugin-1.0.0.zip",
  "sha256": "ab12cd34ef56..."
}
```

字段说明：
- `download_url`: 指向您自己仓库 Release 中 zip 文件的直链
- `sha256`: 上一步计算出的哈希值（**community 插件必填**）
- `min_app_version`: 插件所需的最低 NebulaLab 版本

### 5. 提交并创建 Pull Request

```bash
git add plugins-index.json
git commit -m "feat(plugin): 添加 my-awesome-plugin"
git push origin add-my-awesome-plugin
```

回到 [TshyGO/NebulaLab-Plugins](https://github.com/TshyGO/NebulaLab-Plugins) 创建 Pull Request，在描述中说明插件功能、适用场景和测试情况。

## 版本更新

当您的插件发布新版本时，在自己的仓库发布新 Release 后，向本仓库提交 PR 更新 `plugins-index.json` 中对应条目的 `version`、`download_url` 和 `sha256` 字段即可。

## 审核标准

PR 提交后 CI 会自动校验索引格式，CodeRabbit 会进行 AI 代码审查。维护者将基于以下标准进行最终审核：

- **安全性**: 不应包含恶意代码，不能在未声明的情况下访问文件系统或发起网络请求。
- **稳定性**: 对异常数据和错误参数有适当的容错和错误提示。
- **性能**: 不会在处理常见规模数据时导致应用无响应。
- **UI/UX**: `params_schema` 中定义了对用户友好的参数描述。

通过审核后，您的插件将出现在所有 NebulaLab 用户的插件市场中。

## 疑问与支持

- 提交 [Issue](https://github.com/TshyGO/NebulaLab-Plugins/issues)
- 查阅 [入门指南](./getting_started.md) 获取开发细节
