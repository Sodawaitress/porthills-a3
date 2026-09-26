# 东西都在哪 · 跨机器找文件指南

> 目的：**万一登不上学校那台 Windows（RDP）电脑，也能找到东西、改东西、交作业。**
> 更新：2026-09-26（做完 A3 §7 两张地图之后）

---

## 0. 一句话

**文字/脚本/PNG 在 GitHub；ArcGIS 工程和所有大文件（tif / gdb / shp / pdf）在 OneDrive；
报告 docx 两边都没有，只在另一台机器上。**

---

## 1. 三个位置，各放什么

| 位置 | 路径 | 放什么 | 怎么拿 |
|---|---|---|---|
| **GitHub** | `github.com/Sodawaitress/porthills-a3`（私有） | 所有 `.py` `.md` `.png` `.csv` —— 脚本、报告提纲、制图指南、地图导出的 PNG | `git clone` / `git pull` |
| **OneDrive** | `OneDrive - Lincoln University\ERST619\` | ArcGIS 工程本体 + 全部大文件 | 网页版 OneDrive 或同步客户端 |
| **只在学校那台机器** | `C:\Users\zhouy3d\Desktop\` | 正在用的工作副本（= OneDrive 那份的来源） | RDP 登进去 |

### GitHub 里**没有**的东西（被 `.gitignore` 排除）
`*.tif` `*.shp/.shx/.dbf/.prj` `*.gdb/` `*.zip` `*.pdf` `*.docx`

所以 **ArcGIS 工程（`.aprx` + `.gdb`）、地图的 PDF、报告 docx，git 里一个都没有**。只能走 OneDrive。

---

## 2. OneDrive 里的三份 PortHills（别搞混）

| 文件夹 | 时间 | 是什么 |
|---|---|---|
| `ERST619\PortHills_2026-09-26_maps\` | **2026-09-26（最新）** | **做完 §7 两张地图之后的完整工程**，要用就用这份 |
| `ERST619\PortHills_full_backup\` | 2026-09-21 | 改地图**之前**的快照。万一新版哪里坏了，回退到这份 |
| `Lincoln University\ERST619\PortHills\` | 2026-09-23 | 学校机器上另开的 `a3\2017PortHillsA3.aprx`（"Data cleaning Mask" 那张图在里面）。**注意：它的图层全是断的**，源指向空的 `2017PortHillsA3.gdb`，`PortHills2017_stackA3.tif` 实际在 `a3\` 子目录而不是父目录，图层 `edge_mix` 指向的数据集名拼成了 `dege_mix`。要用得先重连路径 |

---

## 3. A3 §7 地图成果（4 分那项）

### 工程文件
`PortHills2017\PortHills2017.aprx`
备份副本：同目录下 `PortHills2017_backup_2026-09-26_maps.aprx`

### 里面的 Layout

| Layout | 是什么 |
|---|---|
| **`V3_Confidence`** | **Map 1 首选**：燃料分类 + 置信度面板浮在主图右上 + 定位小图 |
| `V3_Confidence_NoLocator` | 同上但不放定位小图（图底注明理由） |
| `V1_Report` | Map 1，报告图 5.6 原配色 |
| `V2_CVDsafe` | Map 1，Okabe-Ito 色盲安全配色 |
| `V4_Terrain` | Map 1，叠 1m LiDAR 山体阴影 |
| **`Map2_Refugia`** | **Map 2**：烧毁程度 4 级 + refugia |
| `Layout` `Layout1` `A3_DataCheck_Layout` `FuelClass_Layout_2017` `Refugia_Layout_2017` | 以前做的，**没动过** |

导出的 PNG（在 git 里）+ PDF（只在 OneDrive）：
`exploration/map_variants/<布局名>.png` / `.pdf`

### 从零重建这些地图
```
关掉 ArcGIS Pro（开着会锁住 aprx，save 会抛 OSError）
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" scripts\44_build_all_maps.py
```
这个脚本会**重建所有同名 Layout**（先删后建），所以在 Pro 里手动调过的东西会被覆盖——手动改完想保住就改脚本，或者把 Layout 另存一个新名字。

### 脚本依赖的数据（都不在 git）
| 用到的 | 在哪 |
|---|---|
| `PortHills2017.gdb\FuelClass_SSp_masked` / `_confidence` | 工程 gdb；源头是 `data\R5_arcgis\*.asc`，由 repo 里的 `R5/08_final_SSp.py` 生成 |
| `PortHills2017.gdb\Severity_2017_map_clipped` | 工程 gdb；由 repo 里的 `scripts/27_build_severity_raster.py` 生成 |
| `data\Port_Hills_2017_Fire_Boundary.shp` | 工程 data 目录 |
| `data\CanterburyRegion.shp` | 从学校 `J:\Data\Administrative_Boundaries\` 拷来的（定位小图用） |
| `PortHills2017\a3\raster\PortHills_HS1m_LiDAR.tif` | 工程里（只有 V4 用） |

---

## 4. 报告 docx —— 两边都没有

`Kaupapa Tuhika 3.docx`（+ `Kaupapa Tuhika 3_BACKUP_1451.docx`）
被 `.gitignore` 的 `*.docx` 排除，**这台学校机器上也没有**（`Desktop\ERST619\A3\` 这个目录在这台机器上不存在）。

按 `STATUS.md` 记的，它在另一台机器上。**换机器之前一定要自己传一份到 OneDrive**，不然改不了。

---

## 5. 换机器要注意的坑

1. **`.aprx` 存的是绝对路径。** 从 OneDrive 复制到别的路径后，图层会全断。修：
   ```python
   aprx.updateConnectionProperties(old_root, new_root)
   ```
   然后**逐个 `arcpy.Exists` 验证**，别假设成功了。
2. **OneDrive 的"按需文件"占位符**会让普通 `Move-Item` / `mv` 中途失败。用 `robocopy /E`。
3. **ArcGIS Pro 开着就存不了 aprx**，`aprx.save()` 抛的是没有说明的 `OSError`。跑脚本前先关 Pro。
4. **这台机器能跑 arcpy**：`C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe`，ArcGIS Pro 3.6.1。（`map_making_guide.md` §3 说这版 arcpy.mp 没有 `createTextElement` —— **那条是错的**，见下。）

---

## 6. 已知问题

- **`map_making_guide.md` §3 路B 第 4 条写错了**：它说"这版 ArcGIS Pro 的 arcpy.mp 没有 `createTextElement` 方法，标题/来源文字框要手动加"。实际 3.6.1 **有**，只是挂在 **project** 对象上不是 layout 上：
  `p.createTextElement(layout, point, "POINT", text, size, font, style, None, name)`
  `44_build_all_maps.py` 里所有标题和来源文字都是脚本生成的，没手打一个字。`report.md` R7 和 `STATUS.md` 里也有同样这句错话，一起改掉。
- **原有 `Map` 里有 3 个图层报断链**：`severity.tif` / `dNBR.tif` / `Extract Bands_stack_fire.tif`，都指向 `data\stack_fire.tif`。那个 tif 文件是在的（1.9 MB，`arcpy.Exists` 为 True），这三个是**栅格函数图层**（on-the-fly 函数链），arcpy 在无界面下常把这类层报成 broken，在 Pro 界面里不一定真坏。**本次两张地图不依赖它们**（用的是 gdb 里已固化的 `Severity_2017_map_clipped`）。在 Pro 里打开 `Map` 看一眼确认；真坏了就重跑 `scripts/27_build_severity_raster.py`，或从 `PortHills_full_backup`（9/21 那份）取回。
- **底图版权文字印在主图里**（"Eagle Technology, LINZ, StatsNZ, NIWA…"）。图层和地图两级的 `attribution` 都清空了，矢量切片底图仍在绘制时自己画出来。要彻底去掉只能不要底图，代价是丢掉 Halswell / Lansdowne / Governors Bay 这些地名。
- **`2024_materials/`** 在 `Desktop\a3\` 里但没被 git 跟踪。2024 年火灾的复现工作当初是**故意**移出这个 repo 的（commit `ad0d454`，"A3 = pure 2017"）。要留就单独处理，别顺手 commit 进来。

---

## 7. 待办

- [ ] Map 1 定稿：`V3_Confidence` 还是 `V3_Confidence_NoLocator`；配色用 V1（跟报告图 5.6 一致）还是 V2（色盲安全）。选 V2 的话报告里的 Fig 5.6 要用同一套颜色重出（改 `R5/08_final_SSp.py` 的 palette）
- [ ] 图题写进 Word，放图**下方**，"Figure X" 加粗（脚本跑完会打印两条现成的）
- [ ] 报告 docx 传一份到 OneDrive
- [ ] 改掉 `map_making_guide.md` / `report.md` R7 / `STATUS.md` 里关于 `createTextElement` 的错话
