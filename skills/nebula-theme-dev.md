---
name: nebula-theme-dev
description: 为 NebulaLab 开发和发布自定义主题的完整指南，包含变量说明、theme.json 模板和发布流程
---

# NebulaLab 主题开发

## 原理

NebulaLab 主题通过覆盖 CSS 变量实现。只需提供想改的变量，未覆盖的变量自动继承内置默认值。

## theme.json 完整字段

```json
{
  "id": "my-theme",          // 必须，唯一 ID，只允许小写字母/数字/连字符/下划线
  "name": "My Theme",        // 显示名称
  "author": "your-name",
  "version": "1.0.0",
  "color_scheme": "dark",    // 必须，"light" 或 "dark"（决定系统 color-scheme）
  "description": "...",
  "background_image_url": "https://...",  // 可选，主题激活时铺在 app 底层的背景图（支持 http/https）
  "variables": {
    "--accent": "#38bdf8",
    "--bg-app": "#0a1628"
    // 只写要覆盖的变量，其余继承内置
  }
}
```

### 背景图说明

- `background_image_url` 为可选字段，必须是 `http://` 或 `https://` 开头的 URL，本地路径会被拒绝
- 背景图铺满整个 app 窗口（`background-size: cover`），固定不随滚动移动
- 推荐托管在 GitHub raw 或可信 CDN 上；社区主题使用外链图片时，图片服务器可获取用户 IP，请在主题说明中告知用户
- 用户若在设置中设置了自己的本地背景图，则会覆盖主题背景
- 未提供此字段的主题行为与之前完全一致

## CSS 变量参考表

### 内置 Light 主题（:root 默认值）

| 变量 | 值 |
|------|-----|
| **背景** | |
| `--bg-app` | `#f0f4f8` |
| `--bg-panel` | `rgba(255,255,255,0.80)` |
| `--bg-subtle` | `rgba(0,0,0,0.02)` |
| `--bg-hover` | `rgba(0,0,0,0.04)` |
| `--bg-input` | `rgba(255,255,255,0.9)` |
| `--bg-panel-strong` | `rgba(255,255,255,0.98)` |
| **边框** | |
| `--border` | `rgba(0,0,0,0.06)` |
| `--border-strong` | `rgba(0,0,0,0.12)` |
| `--border-shine` | `rgba(255,255,255,1)` |
| **文字** | |
| `--text-primary` | `#0f172a` |
| `--text-secondary` | `#374151` |
| `--text-muted` | `#6b7280` |
| `--text-placeholder` | `#9ca3af` |
| **海军蓝** | |
| `--navy` | `#1e3a5f` |
| `--navy-dark` | `#132642` |
| `--navy-hover` | `#254a78` |
| **强调色** | |
| `--accent` | `#c8622e` |
| `--accent-hover` | `#b05226` |
| `--accent-strong` | `#a84e22` |
| `--accent-soft` | `rgba(200,98,46,0.10)` |
| `--accent-glow` | `rgba(200,98,46,0.20)` |
| **状态色** | |
| `--success` | `#16a34a` |
| `--success-soft` | `rgba(22,163,74,0.12)` |
| `--danger` | `#dc2626` |
| `--danger-soft` | `rgba(220,38,38,0.10)` |
| `--warning` | `#d97706` |
| **阴影** | |
| `--shadow-xs` | `0 1px 2px rgba(0,0,0,0.06)` |
| `--shadow-sm` | `0 1px 3px rgba(0,0,0,0.08)` |
| `--shadow-md` | `0 4px 12px rgba(0,0,0,0.08)` |
| `--shadow-panel` | `0 2px 8px rgba(0,0,0,0.06)` |
| `--shadow-lift` | `0 4px 16px rgba(0,0,0,0.10)` |
| `--shadow-accent` | `0 4px 14px rgba(200,98,46,0.28)` |
| `--shadow-inset` | `inset 0 1px 0 rgba(255,255,255,0.60)` |
| **圆角** | |
| `--radius-full` | `9999px` |
| `--radius-xl` | `16px` |
| `--radius-lg` | `12px` |
| `--radius-md` | `8px` |
| `--radius-sm` | `6px` |
| `--radius-xs` | `4px` |
| **字体** | |
| `--font-ui` | `'Segoe UI Variable Text', 'Segoe UI', -apple-system, sans-serif` |
| `--font-display` | `'Segoe UI Variable Display', 'Segoe UI', -apple-system, sans-serif` |
| `--font-mono` | `'Cascadia Code', 'Fira Code', monospace` |

### 内置 Dark 主题（graphite-dark 默认值）

| 变量 | 值 |
|------|-----|
| **背景** | |
| `--bg-app` | `#0d1520` |
| `--bg-panel` | `rgba(18,24,38,0.75)` |
| `--bg-subtle` | `rgba(255,255,255,0.04)` |
| `--bg-hover` | `rgba(255,255,255,0.08)` |
| `--bg-input` | `rgba(0,0,0,0.4)` |
| `--bg-panel-strong` | `rgba(26,34,51,0.85)` |
| **边框** | |
| `--border` | `rgba(255,255,255,0.08)` |
| `--border-strong` | `rgba(255,255,255,0.15)` |
| `--border-shine` | `rgba(255,255,255,0.12)` |
| **文字** | |
| `--text-primary` | `#e2e8f4` |
| `--text-secondary` | `#94a3b8` |
| `--text-muted` | `#4a5a72` |
| `--text-placeholder` | `#3a4a60` |
| **海军蓝** | |
| `--navy` | `#162438` |
| `--navy-dark` | `#0d1825` |
| `--navy-hover` | `#1e3050` |
| **强调色** | |
| `--accent` | `#e07840` |
| `--accent-hover` | `#f08840` |
| `--accent-strong` | `#f08840` |
| `--accent-soft` | `rgba(224,120,64,0.12)` |
| `--accent-glow` | `rgba(224,120,64,0.20)` |
| **状态色** | |
| `--success` | `#22c55e` |
| `--success-soft` | `rgba(34,197,94,0.14)` |
| `--danger` | `#f87171` |
| `--danger-soft` | `rgba(248,113,113,0.12)` |
| `--warning` | `#fbbf24` |
| **阴影** | |
| `--shadow-xs` | `0 1px 2px rgba(0,0,0,0.30)` |
| `--shadow-sm` | `0 2px 7px rgba(0,0,0,0.38)` |
| `--shadow-md` | `0 6px 20px rgba(0,0,0,0.44)` |
| `--shadow-panel` | `0 2px 8px rgba(0,0,0,0.25)` |
| `--shadow-lift` | `0 4px 16px rgba(0,0,0,0.40)` |
| `--shadow-accent` | `0 6px 24px rgba(224,120,64,0.30)` |
| `--shadow-inset` | `inset 0 1px 0 rgba(255,255,255,0.04)` |

## 实用建议

- **深色主题**：`color_scheme: "dark"`，重点覆盖 `--bg-*`、`--text-*`、`--accent`、`--border`
- **浅色主题**：`color_scheme: "light"`，同上
- **只改强调色**：覆盖 `--accent`、`--accent-hover`、`--accent-strong`、`--accent-soft`、`--accent-glow`、`--shadow-accent` 六个变量即可换一套主色调
- **调整圆角风格**：覆盖 `--radius-*` 变量统一调整界面圆角（更圆/更方）

## 打包格式

```bash
cd my-theme/
zip -r my-theme-1.0.0.zip .
# zip 根目录直接包含 theme.json
```

或包一层同名目录：

```
my-theme-1.0.0.zip
└── my-theme/
    └── theme.json
```

## 发布到主题市场

1. 在自己的 GitHub 仓库发布 Release，上传 zip
2. 计算 sha256：
   - macOS/Linux：`shasum -a 256 my-theme.zip`
   - Windows：`Get-FileHash my-theme.zip -Algorithm SHA256`
3. Fork TshyGO/NebulaLab-Plugins，在 `themes-index.json` 的 `themes` 数组末尾添加：
   ```json
   {
     "id": "my-theme",
     "name": "My Theme",
     "author": "your-name",
     "version": "1.0.0",
     "source": "community",
     "color_scheme": "dark",
     "description": "...",
     "download_url": "https://github.com/you/repo/releases/download/v1.0.0/my-theme.zip",
     "sha256": "abc123...",
     "homepage": "https://github.com/you/repo",
     "preview_image_url": "https://raw.githubusercontent.com/you/repo/main/preview.png",
     "background_image_url": "https://...",
     "min_app_version": "0.7.1",
     "tags": ["dark", "nebula", "high-contrast"],
     "accessibility_notes": "Primary text keeps AA contrast on panels."
   }
   ```
   `background_image_url` 为可选字段，有背景图的主题在市场卡片上会显示"含背景图"标识。
4. 提交 PR（只修改 `themes-index.json`，不能包含其他文件），CI 会下载 release zip 校验哈希和 `theme.json`，通过后自动合并

**重要提示**：发布到市场时，所有字段都是必填项，包括 `sha256`、主页、预览图、标签、最低版本和可访问性说明。CI 验证会拒绝缺少任何必填字段的条目。
