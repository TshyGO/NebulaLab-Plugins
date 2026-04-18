# 贡献指南

感谢您有兴趣为 NebulaLab 插件市场贡献力量！社区插件采用**去中心化**模式——您的插件代码托管在自己的仓库中，只需向本仓库提交一条索引记录，审核通过后即可在所有用户的插件市场中展示。

## 提交前准备

在提交之前，请确保完成以下检查：

1. **功能完整且无 Bug**: 在本地或 NebulaLab 客户端中充分测试，确保插件在正常和异常输入下都能正确运行。
2. **完整的 `plugin.json`**:
   - `id`: 全局唯一标识符，只允许小写字母、数字、连字符和下划线（例如 `yourname-awesome-plugin`）。
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

所有远端市场插件都必须提供 zip 文件的 sha256 校验值，用于安装时的完整性验证：

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
  "homepage": "https://github.com/您的用户名/my-awesome-plugin",
  "logo_url": "https://raw.githubusercontent.com/您的用户名/my-awesome-plugin/main/assets/logo.png",
  "source_url": "https://github.com/您的用户名/my-awesome-plugin",
  "sha256": "ab12cd34ef56..."
}
```

字段说明：
- `download_url`: 指向您自己仓库 Release 中 zip 文件的直链
- `homepage`: 插件主页或项目介绍页（**所有插件必填**）
- `logo_url`: 插件卡片徽标（**可选**，建议使用透明底方形图片）
- `source_url`: 插件源码仓库地址（**community 插件必填**）
- `sha256`: 上一步计算出的哈希值（**所有远端市场插件必填**）
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

## 审核流程

PR 提交后 CI 会自动进行验证：

1. **文件检查**: 确认 PR 只修改了 `plugins-index.json`（代码变更需要人工审核）
2. **格式验证**: 校验索引文件的 JSON 格式和字段完整性
3. **远端资产验证**: 下载 `download_url` 指向的 zip，校验 sha256 与 `plugin.json`
4. **基础风险扫描**: 对 release zip 内的 Python 代码做启发式危险模式检查

全部验证通过后，PR 将自动 squash merge，通常在几分钟内完成。

**重要说明**：自动化验证并不等于人工安全审计。我们会验证声明与 release 内容是否一致，但不会替代开发者和用户的独立代码审查。

**验证失败处理**: 失败原因会在 PR 页面显示具体错误信息。按提示修改后重新 push，CI 会重新运行验证。

通过审核后，您的插件将出现在所有 NebulaLab 用户的插件市场中。

## 提交主题到主题市场

NebulaLab 支持用户自定义主题，您可以将自己设计的主题分享给所有用户。

### 主题 zip 格式

主题需要打包为以下结构：

```
my-theme-1.0.0.zip
└── my-theme/
    └── theme.json
```

### theme.json 必填字段

```json
{
  "id": "my-theme",
  "name": "My Theme",
  "author": "your-name",
  "version": "1.0.0",
  "color_scheme": "light",
  "description": "...",
  "background_image_url": "https://...",
  "variables": {
    "--bg-app": "#ffffff",
    "--accent": "#e07840"
  }
}
```

字段说明：
- `id`: 主题唯一标识符，只允许小写字母、数字、连字符和下划线
- `color_scheme`: `"light"` 或 `"dark"`
- `background_image_url`: **可选**，主题激活时铺在 app 底层的背景图，必须是 `http://` 或 `https://` URL；使用外链图片时，图片服务器可获取用户 IP，请在主题说明中告知用户
- `variables`: CSS 变量覆盖，只需要提供想覆盖的变量，未覆盖的变量继承内置默认值

完整 CSS 变量列表参考内置主题的两个区块（`:root` 和 `:root[data-theme='graphite-dark']`）。

### 提交流程

流程与插件提交完全一致：

1. **在自己的仓库发布 Release**: 将主题打包为 zip 文件，发布 Release
2. **计算 sha256**:
   ```bash
   # macOS / Linux
   shasum -a 256 my-theme-1.0.0.zip
   
   # Windows PowerShell
   Get-FileHash my-theme-1.0.0.zip -Algorithm SHA256
   ```
3. **Fork 仓库并修改 themes-index.json**: 在 `themes` 数组末尾加入条目
   ```json
   {
     "id": "my-theme",
     "name": "My Theme",
     "version": "1.0.0",
     "author": "your-name",
     "source": "community",
     "color_scheme": "light",
     "description": "A clean warm-light theme for spectroscopy work",
     "download_url": "https://github.com/you/my-theme/releases/download/v1.0.0/my-theme-1.0.0.zip",
     "sha256": "abc123...",
     "homepage": "https://github.com/you/my-theme",
     "preview_image_url": "https://raw.githubusercontent.com/you/my-theme/main/preview.png",
     "background_image_url": "https://...",
     "min_app_version": "0.7.1",
     "tags": ["light", "warm", "lab"],
     "accessibility_notes": "Body text contrast >= WCAG AA on panels."
   }
   ```
   `background_image_url` 为可选字段，有背景图的主题在市场卡片上会显示"含背景图"标识。
4. **提交 PR**: CI 自动下载 release zip，校验 sha256 和 `theme.json`，通过后自动 squash merge，几分钟内上架

注意：PR 只能修改 `themes-index.json`，不能包含其他文件，否则 CI 拒绝。

## 疑问与支持

- 提交 [Issue](https://github.com/TshyGO/NebulaLab-Plugins/issues)
- 查阅 [入门指南](./getting_started.md) 获取开发细节
