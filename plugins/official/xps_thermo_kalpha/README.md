# Thermo Scientific K-Alpha XPS

该官方插件用于导入 Thermo Scientific K-Alpha / Avantage 导出的 XPS Excel 工作簿，解决通用 importer 将仪器导出文件误判为空表的问题。

## 支持格式

- `.xls`
- `.xlsx`

典型导出目录：

```text
1.xls
C1s Scan.VGD
O1s Scan.VGD
Si2p Scan.VGD
Ti2p Scan.VGD
XPS Survey.VGD
Zn2p Scan.VGD
```

第一版优先解析 `1.xls`。`.VGD` 是 OLE/compound 二进制文件，不走通用文本导入逻辑。

## 导入行为

插件不会把多个 scan sheet 合并成长表。导入一个 workbook 后，Nebula Lab 会在同一个原始数据分组中创建多个数据项：

- 第一个有效谱图 sheet 作为主表；
- 其他谱图 sheet 通过 `extra_tables` 创建独立数据项；
- `Peak Table` 会作为独立数据项导入；
- `Titles` 如果非空，也会作为独立数据项导入。

数据项名称按 `文件名·sheet名` 生成，例如 `1·Zn2p Scan`、`1·XPS Survey`、`1·Peak Table`。插件会在 `ImportResult.meta["display_name_by_table"]` 中提供每个附加表的完整显示名，避免 Nebula Lab 将第一张 sheet 名重复拼接到其他 sheet 上。

每个谱图 sheet 输出列：

```text
binding_energy_eV
intensity_cps
background_cps
corrected_intensity_cps
source_sheet
source_file
```

## Metadata

插件会尽量提取每个 scan sheet 右侧的采集参数，例如：

- `Total acquisition time`
- `Number of Scans`
- `Source Gun Type`
- `Spot Size`
- `Lens Mode`
- `Analyser Mode`
- `Energy Step Size`
- `Number of Energy Steps`

这些信息保存在 `ImportResult.meta["region_metadata"]` 中。

## 附加操作

插件提供两个轻量 XPS 操作：

- `xps_normalize_intensity`：强度归一化；
- `xps_calibrate_binding_energy`：结合能轴平移校准，默认参考 C 1s = 284.8 eV。