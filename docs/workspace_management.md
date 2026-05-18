# NebulaLab 插件工作区管理

## 推荐定位

`NebulaLab-Plugins` 是官方插件 monorepo 和插件市场仓库：

- `plugins/official/` 存放官方插件源码。
- `plugins-index.json` 是应用读取的插件市场索引。
- GitHub Release 的 `plugins` 标签存放官方插件 zip。
- `nebula_sdk/`、`templates/`、`docs/`、`skills/` 提供开发工具和文档。

`Data_Process` 是 NebulaLab 主应用仓库，只负责插件运行时、市场 UI、安装、加载和联调。

## 本地目录

建议两个仓库并列放置：

```text
E:\Antigravity_Workshop\
  Data_Process\
  NebulaLab-Plugins\
```

这样 Git 状态不会互相污染，也方便 IDE 同时打开两个仓库。

本仓库根目录提供 `NebulaLab.code-workspace`，当两个仓库按上面目录并列时，可以直接用 VS Code 打开。

## 换电脑恢复

如果只做插件开发，clone 插件仓库即可：

```powershell
cd E:\Antigravity_Workshop
git clone https://github.com/TshyGO/NebulaLab-Plugins.git
```

如果要做主应用和插件联调，需要 clone 两个仓库：

```powershell
cd E:\Antigravity_Workshop
git clone https://github.com/TshyGO/NebulaLab.git Data_Process
git clone https://github.com/TshyGO/NebulaLab-Plugins.git
code NebulaLab-Plugins\NebulaLab.code-workspace
```

如果主应用远端名称不同，以实际 `Data_Process` 仓库 URL 为准。

## 官方插件发布流程

1. 修改 `plugins/official/<plugin_folder>/`。
2. 运行插件仓库测试：

   ```powershell
   python -m pytest -q
   ```

3. 打包插件并更新索引：

   ```powershell
   python scripts/package_official_plugin.py bet-tristar --update-index
   ```

4. 上传 zip 到 GitHub Release：

   ```powershell
   gh release upload plugins dist\plugins\bet-tristar-0.1.0.zip --repo TshyGO/NebulaLab-Plugins --clobber
   ```

5. 提交并推送源码与索引：

   ```powershell
   git add plugins/official plugins-index.json
   git commit -m "feat(plugin): update bet-tristar"
   git push
   ```

## 什么时候拆独立插件仓库

官方插件默认不拆仓库，统一放在 `plugins/official/`。

只有在插件需要独立团队、独立权限、独立 CI、或不适合公开源码时，才考虑单独仓库。社区插件仍然使用去中心化模式：源码在作者自己的仓库，`NebulaLab-Plugins` 只维护市场索引。
