# ALS Baseline Correction / ALS 基线校正

This official plugin applies asymmetric least squares (ALS) baseline correction to a numeric signal column. It is useful for spectroscopy-style preprocessing where slow baseline drift needs to be removed before later analysis.

这个官方插件使用非对称最小二乘法（ALS）对数值信号列进行基线校正，适合光谱等场景下的预处理，用于去除缓慢变化的背景基线。

## Parameters / 参数说明

- `y_column`: The numeric column to correct. 要校正的数值列。
- `lam`: Smoothing factor. Larger values produce a smoother baseline. 平滑参数，越大基线越平滑。
- `p`: Asymmetry parameter, usually a small value such as `0.01`. 不对称参数，通常取较小值。
- `niter`: Number of ALS iterations. ALS 迭代次数。

## Output / 输出结果

- The selected `y_column` is replaced with the baseline-corrected signal.
- A new column named `<y_column>_baseline` is added for inspection.

- 选中的 `y_column` 会被替换为校正后的结果。
- 会额外新增一列 `<y_column>_baseline`，用于查看估计出的基线。

## Example / 使用示例

```python
params = {
    "y_column": "intensity",
    "lam": 1e5,
    "p": 0.01,
    "niter": 10,
}
```

After loading the plugin in the app, select `ALS 基线校正` from the `Plugin Operations` panel and fill in the parameters above.

把插件放入应用的 `plugins/` 目录并启动后，在 `Plugin Operations` 面板中选择 `ALS 基线校正`，再填写以上参数即可执行。
