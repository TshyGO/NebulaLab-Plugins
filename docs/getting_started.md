# Getting Started / 快速开始

This guide gets you from template to a running NebulaGraph plugin in about five minutes.

这份指南帮助你在大约 5 分钟内，从模板开始做出一个可运行的 NebulaGraph 插件。

## 1. Copy the template / 复制模板

Copy `templates/plugin_template/` to a new local folder and rename it to your plugin name.

把 `templates/plugin_template/` 复制到本地新目录，并改成你的插件名称。

## 2. Edit `plugin.json` and `__init__.py` / 修改 `plugin.json` 和 `__init__.py`

Update the metadata in `plugin.json`, then implement your operation logic inside `__init__.py`.

先修改 `plugin.json` 中的元数据，再在 `__init__.py` 里实现你的操作逻辑。

## 3. Put the plugin into the app / 放入应用插件目录

Copy your finished plugin folder into the application's `plugins/` directory.

把完成后的插件目录复制到应用的 `plugins/` 目录中。

## 4. Restart the app / 重启应用

Restart the NebulaGraph application so it can scan the `plugins/` directory and load your plugin automatically.

重启 NebulaGraph 应用，程序会自动扫描 `plugins/` 目录并加载你的插件。

## 5. Run it from the UI / 在界面中执行

Open the `Plugin Operations` panel, find your operation, fill in the parameters, and run it.

打开 `Plugin Operations` 面板，找到你的操作，填写参数后执行即可。

## 6. UI 插件面板（可选）/ UI Plugin Panel (Optional)

如果你的插件需要自定义可视化界面，可以添加 UI 面板：

### 创建 panel.html

在插件目录下创建 `panel.html` 文件，实现你的自定义 UI 界面。

### 修改 plugin.json

在 `plugin.json` 中添加 `panel` 字段，指定面板文件：

```json
{
  "id": "my-plugin",
  "panel": "panel.html",
  ...
}
```

### 通信协议

`panel.html` 运行在 sandbox iframe 中，通过 `postMessage` 与主程序通信：

**向主程序发送请求：**
```javascript
window.parent.postMessage({
  type: 'PLUGIN_REQUEST',
  action: 'GET_SAMPLE_INFO',
  payload: { /* 可选参数 */ }
}, '*');
```

**接收主程序响应：**
```javascript
window.addEventListener('message', (e) => {
  if (e.data.type === 'PLUGIN_RESPONSE') {
    const { sampleId, columns } = e.data.payload;
    // 处理返回的数据
  }
});
```

### 安全提示

`panel.html` 运行在 sandbox iframe 中，无法访问本地文件系统和主程序存储，只能通过 `postMessage` 协议与主程序通信。
