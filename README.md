# NebulaLab-Plugins

[中文](#中文) | [English](#english)

---

<a name="中文"></a>

## 简介

这是 NebulaLab 的插件生态仓库，包含官方插件、插件市场索引、开发 SDK 和开发文档。

## 安装插件和主题（用户）

直接在 NebulaLab 应用里操作，无需访问本仓库：

- **社区 → 插件广场** → 浏览并安装插件（联网）
- **社区 → 主题广场** → 浏览并安装自定义主题（联网）
- **插件管理** → 从本地安装插件 `.zip` 文件
- **设置** → 从本地安装主题 `.zip` 文件

## 开发插件

三个入口：

| 文档 | 说明 |
|------|------|
| [快速开始](./docs/getting_started.md) | 从环境搭建到第一个插件 |
| [SDK API 参考](./docs/api_reference.md) | `@op` 装饰器、`OperationContext` 详解 |
| [Claude Code Skill](./skills/nebula-plugin-dev.md) | AI 辅助开发插件 |

## 开发主题

| 文档 | 说明 |
|------|------|
| [Claude Code Skill](./skills/nebula-theme-dev.md) | AI 辅助设计主题，含完整 CSS 变量参考表 |
| [贡献指南 · 主题部分](./docs/contributing.md#提交主题到主题市场) | 主题打包与发布流程 |

## 提交到插件市场

流程详见 [贡献指南](./docs/contributing.md)。核心步骤：

1. 在自己的仓库发布插件 Release（zip 包）
2. 计算 sha256 校验值
3. Fork 本仓库，在 `plugins-index.json` 添加条目
4. 提交 PR — CI 自动验证，通过后自动合并

## 提交到主题市场

1. 在自己的仓库发布主题 Release（zip 包，内含 `theme.json`）
2. 计算 sha256 校验值
3. Fork 本仓库，在 `themes-index.json` 添加条目
4. 提交 PR — CI 自动验证，通过后自动合并

## 仓库结构

```
NebulaLab-Plugins/
├── plugins-index.json          # 插件市场索引（应用直接读取）
├── themes-index.json           # 主题市场索引（应用直接读取）
├── plugins/official/           # 官方插件
├── nebula_sdk/                 # 插件开发 SDK（Python 包）
├── templates/plugin_template/  # 插件开发模板
├── docs/                       # 开发文档
│   ├── getting_started.md      # 插件入门指南
│   ├── api_reference.md        # SDK API 参考
│   └── contributing.md         # 贡献指南（插件 + 主题）
├── skills/                     # AI 辅助开发 skill
│   ├── nebula-plugin-dev.md    # 插件开发 skill
│   └── nebula-theme-dev.md     # 主题开发 skill
└── .github/workflows/          # CI：PR 时自动验证格式并合并
```

---

<a name="english"></a>

## Overview

This is the plugin ecosystem repository for NebulaLab, containing official plugins, plugin marketplace index, development SDK, and documentation.

## Installing Plugins and Themes (Users)

Install directly in the NebulaLab app — no need to visit this repository:

- **Community → Plugin Store** → Browse and install plugins (online)
- **Community → Theme Store** → Browse and install custom themes (online)
- **Plugin Manager** → Install plugin from local `.zip` file
- **Settings** → Install theme from local `.zip` file

## Developing Plugins

| Document | Description |
|----------|-------------|
| [Getting Started](./docs/getting_started.md) | From setup to your first plugin |
| [SDK API Reference](./docs/api_reference.md) | `@op` decorator, `OperationContext` details |
| [Claude Code Skill](./skills/nebula-plugin-dev.md) | AI-assisted plugin development |

## Developing Themes

| Document | Description |
|----------|-------------|
| [Claude Code Skill](./skills/nebula-theme-dev.md) | AI-assisted theme design with full CSS variable reference |
| [Contributing Guide · Themes](./docs/contributing.md#提交主题到主题市场) | Theme packaging and publishing |

## Submitting to the Marketplace

See [Contributing Guide](./docs/contributing.md) for full details. Key steps:

**Plugins:** Fork → add entry to `plugins-index.json` → submit PR — CI auto-validates and merges.

**Themes:** Fork → add entry to `themes-index.json` → submit PR — CI auto-validates and merges.

## Repository Structure

```
NebulaLab-Plugins/
├── plugins-index.json          # Plugin marketplace index (read by the app)
├── themes-index.json           # Theme marketplace index (read by the app)
├── plugins/official/           # Official plugins
├── nebula_sdk/                 # Plugin development SDK (Python package)
├── templates/plugin_template/  # Plugin template
├── docs/                       # Documentation
│   ├── getting_started.md      # Getting started guide
│   ├── api_reference.md        # API reference
│   └── contributing.md         # Contributing guide (plugins + themes)
├── skills/                     # AI-assisted development skills
│   ├── nebula-plugin-dev.md    # Plugin development skill
│   └── nebula-theme-dev.md     # Theme development skill
└── .github/workflows/          # CI: Auto-validate and merge on PR