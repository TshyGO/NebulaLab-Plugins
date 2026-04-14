# Contributing Community Plugins / 社区插件贡献流程

This repository accepts community plugin listings through `plugins-index.json`. The plugin code itself stays in your own GitHub repository.

这个仓库通过 `plugins-index.json` 接收社区插件条目；插件代码本身由开发者维护在自己的 GitHub 仓库中。

## Workflow (Option 2) / 流程（方案二）

1. Create and maintain your plugin in your own GitHub repository.

自己创建 GitHub 仓库，开发并维护你的插件代码。

2. Make sure your repository has GitHub Releases, and the release zip contains the plugin directory itself with `plugin.json` and `__init__.py`. For UI plugins, also include `panel.html`.

确保你的仓库发布了 GitHub Releases，并且 zip 包中直接包含插件目录本身，目录内至少有 `plugin.json` 和 `__init__.py`。UI 插件还需要包含 `panel.html`。

3. Open a pull request to this repository and modify only `plugins-index.json` to add your plugin entry.

向本仓库提交 PR，并且只修改 `plugins-index.json`，新增你的插件条目。

4. In your entry, set `source` to `community` and set `download_url` to the release zip URL from your own repository. For UI plugins, also add `"panel": true` to indicate the plugin has a custom panel.

在条目中把 `source` 填为 `community`，并把 `download_url` 填成你自己仓库 Release 的 zip 下载链接。UI 插件还需添加 `"panel": true` 字段表示该插件含自定义面板。

5. Review checks focus only on three things: valid format, accessible `download_url`, and whether the plugin can be loaded successfully.

审核只检查三件事：格式是否正确、`download_url` 是否可访问、插件是否能正常加载。

6. After the PR is merged, the plugin becomes available in the marketplace for app users.

PR 合并后，插件就会上线，应用用户可以在插件市场中看到它。

## Notes / 说明

- Keep the plugin code outside this repository. Do not submit your full plugin implementation here unless it is an official plugin maintained by the NebulaGraph team.
- Update your own repository and Releases when shipping new versions.
- Make sure the metadata in `plugins-index.json` matches your released package.

- 社区插件代码应放在你自己的仓库里；除非是官方维护插件，否则不要把完整实现提交到这里。
- 发布新版本时，请同步更新你自己的仓库和 Releases。
- 请确保 `plugins-index.json` 中的元数据与你发布的 zip 包一致。
