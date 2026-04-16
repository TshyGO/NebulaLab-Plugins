# NebulaLab-Plugins

[中文](#中文) | [English](#english)

---

<a name="中文"></a>

## 简介

这是 NebulaLab 的插件生态仓库，包含官方插件、插件市场索引、开发 SDK 和开发文档。

## 安装插件（用户）

直接在 NebulaLab 应用里操作，无需访问本仓库：

- **插件广场** → 浏览并安装（联网）
- **插件管理** → 从本地安装 `.zip` 文件

## 开发插件

三个入口：

| 文档 | 说明 |
|------|------|
| [快速开始](./docs/getting_started.md) | 从环境搭建到第一个插件 |
| [SDK API 参考](./docs/api_reference.md) | `@op` 装饰器、`OperationContext` 详解 |
| [Claude Code Skill](./skills/nebula-plugin-dev.md) | AI 辅助开发 |

### AI 辅助开发

加载 skill 后，直接告诉 Claude 你要做什么功能：

```bash
claude --add-skill https://raw.githubusercontent.com/TshyGO/NebulaLab-Plugins/main/skills/nebula-plugin-dev.md
```

## 提交到插件市场

流程详见 [贡献指南](./docs/contributing.md)。核心步骤：

1. 在自己的仓库发布插件 Release（zip 包）
2. 计算 sha256 校验值
3. Fork 本仓库，在 `plugins-index.json` 添加条目
4. 提交 PR

## 仓库结构

```
NebulaLab-Plugins/
├── plugins-index.json          # 插件市场索引（应用直接读取）
├── plugins/official/           # 官方插件
├── nebula_sdk/                 # 插件开发 SDK（Python 包）
├── templates/plugin_template/  # 插件开发模板
├── docs/                       # 开发文档
│   ├── getting_started.md      # 入门指南
│   ├── api_reference.md        # API 参考
│   └── contributing.md         # 贡献指南
├── skills/                     # AI 辅助开发
│   └── nebula-plugin-dev.md    # Claude Code skill
└── .github/workflows/          # CI：PR 时自动验证插件格式
```

---

<a name="english"></a>

## Overview

This is the plugin ecosystem repository for NebulaLab, containing official plugins, plugin marketplace index, development SDK, and documentation.

## Installing Plugins (Users)

Install directly in the NebulaLab app — no need to visit this repository:

- **Plugin Store** → Browse and install (online)
- **Plugin Manager** → Install from local `.zip` file

## Developing Plugins

Three entry points:

| Document | Description |
|----------|-------------|
| [Getting Started](./docs/getting_started.md) | From setup to your first plugin |
| [SDK API Reference](./docs/api_reference.md) | `@op` decorator, `OperationContext` details |
| [Claude Code Skill](./skills/nebula-plugin-dev.md) | AI-assisted development |

### AI-Assisted Development

Load the skill, then simply tell Claude what feature you want:

```bash
claude --add-skill https://raw.githubusercontent.com/TshyGO/NebulaLab-Plugins/main/skills/nebula-plugin-dev.md
```

## Submitting to the Marketplace

See [Contributing Guide](./docs/contributing.md) for full details. Key steps:

1. Publish a Release (zip) in your own repository
2. Calculate sha256 checksum
3. Fork this repo, add an entry to `plugins-index.json`
4. Submit a PR

## Repository Structure

```
NebulaLab-Plugins/
├── plugins-index.json          # Marketplace index (read by the app)
├── plugins/official/           # Official plugins
├── nebula_sdk/                 # Plugin development SDK (Python package)
├── templates/plugin_template/  # Plugin template
├── docs/                       # Documentation
│   ├── getting_started.md      # Getting started guide
│   ├── api_reference.md        # API reference
│   └── contributing.md         # Contributing guide
├── skills/                     # AI-assisted development
│   └── nebula-plugin-dev.md    # Claude Code skill
└── .github/workflows/          # CI: Auto-validate plugin format on PR