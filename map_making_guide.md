# 地图制作指南 · 照抄用（map making guide）

> 学习/规划笔记，非提交正文。一站式：**rubric 要什么 + 我实际怎么做 + 标准模板**。
> A4 和以后做地图直接照抄这份。更新：2026-09-26

---

## 0. 一句话
GEE 负责**算 + 出底图影像**，ArcGIS Pro 负责**排版加 6 要素**。评分看的是排版那一步，别只丢个 GEE 截图。

---

## 1. 评分标准要什么（graders 的打分点）

### 1a. A2 简报 "Map Requirements"（5 个维度，逐条对）
1. **Map Purpose** — 版面/清晰度/设计要让人一眼看懂这图**要传达什么**。
2. **Map Elements（6 要素，1–6 分）**：**Title / Legend / Scale bar / North arrow / Inset map(定位图) / Source notes(含 projection)**。
   - ⚠️ 某个要素故意不放 → **必须在图底注一句理由**，不能默默省掉。
3. **Symbology** — 配色合适易读；线/点大小得当；要素之间清楚区分；**重点突出、不杂乱**；符号服务地图目的。
4. **Font / Typography** — 清晰的**字体层级**(标题 vs 标签)。
5. **Visual Hierarchy** — 逻辑清晰、好跟读的版面。

### 1b. Helen 对 A1 图件的反馈（L7，别再犯的坑）
- 图/表前要有**一句正文引出它**（"如 Figure X 所示…"）。
- **表标题在表上方，图标题在图下方**。
- caption 要 **stand-alone**：不看正文也能看懂这张图在讲什么。
- caption 里 **"Figure X" / "Table X" 加粗**，其余文字正常。
- **定位小图(inset)只放第一张地图**，第二、三张不重复。
- **指北针的样式 + 位置，所有地图保持一致**。

---

## 2. 必备元素清单（做每张图打勾）

| 要素 | 要点 |
|---|---|
| ☐ **Title** | 什么变量 + 哪里 + 什么时间（"Pre-fire fuel classes, Port Hills, 2017"） |
| ☐ **Legend** | 类别颜色块 + 文字；对色盲友好(别红绿并列) |
| ☐ **Scale bar** | 用**条形**比例尺，不用 "1:xxxx" 文字比例(缩放会失真) |
| ☐ **North arrow** | 简洁；**所有图样式+位置一致**(Helen 点名) |
| ☐ **Inset / locator** | 大范围(NZ/Canterbury)圈出 AOI；**只第一张图放** |
| ☐ **Source + projection** | 图底小字：数据源(Landsat 8 / LCDB) + **EPSG:2193 (NZTM)** |
| ☐ **Caption** | 图**下方**，stand-alone，"Figure X" 加粗 |
| ☐ 省略任何要素 | 图底注明理由 |

---

## 3. 我的做图流程（两条路，照抄）

### 路 A — GEE 出底图/栅格（A2 用的）
1. 算指数/分类：dNBR、severity、truecolour/SWIR 组合等，定 **palette**：
   - dNBR：`['0000ff','ffffff','ffff00','ff8000','ff0000']`（蓝-白-黄-橙-红）
   - severity(RdYlGn)：`['1a9850','ffffbf','fdae61','d73027']`（绿-黄-橙-红）
   - ⚠️ 缩放系数别漏：Landsat C2L2 `×0.0000275 − 0.2`；S2 `/10000`
2. 裁到 AOI，投影 **EPSG:2193**。
3. 导出：`ee.batch.Export.image.toDrive(image=…, region=aoi, scale=…, crs='EPSG:2193')`，或小图用 `getThumbURL`。
4. 脚本参考：`A2/scripts/01_dNBR_2024_PortHills.py`（dNBR/severity + palette + export）。
5. ⚠️ **GEE 导的只是底图影像，没有 legend/scale/N-arrow/inset** —— 这些要进 ArcGIS Pro 加（路 B）。

### 路 B — ArcGIS Pro 排版（A3 用的，最终地图都走这条）
1. 栅格/矢量加进 Map，坐标系设 **EPSG:2193 (NZTM)**。
2. 新建 **Layout**，摆上 §2 的 6 要素。
3. 版面按老师反馈排（见 §4）。
4. 全自动脚本参考：`A3/scripts/44_build_all_maps.py`（重建所有 Layout，标题/来源文字全脚本生成）、
   `45_build_cleaning_map.py`（Map3 清洗图）、`27_build_severity_raster.py`（severity 栅格）。
   - ✅ **标题/来源文字框能用脚本加**：ArcGIS Pro 3.6.1 的 `createTextElement` 挂在 **project** 对象上(不是 layout)：
     `p.createTextElement(layout, point, "POINT", text, size, font, style, None, name)`。44 号脚本里所有标题+来源都是脚本打的，没手打一个字。
5. 导出 **File → Export Layout**，四周**留白别贴边**。

---

## 4. 老师对布局的反馈（A4 照这个排）

> "move the **main map to the left**, and place the **inset map, legend and scale bar all on the right** along with the **N arrow**. Be careful you have **slightly cut off the left of the inset map, legend and scale bar**."

拆成两条：
1. **重排**：主图挪左边占最大块 → 右侧**竖排**放 inset / N 指北针 / 图例 / 比例尺，全部**左对齐**。
2. **修 bug**：inset/图例/比例尺**左边被裁了一点** → Pro 里用 Guides 拉参考线对齐 + 留够页边距。

**为什么好看**：主图是主角(视线从左进入→放左边给最大空间)；辅助元素是配角，全收右列、左对齐成一条隐形竖线，不跟主图抢注意力，留白也规整。

---

## 5. 标准版面模板（ASCII 草图，照摆）

```
+---------------------------------------------------+
| Map 1 — Pre-fire fuel classes, Port Hills 2017    |  <- 标题
| +-----------------------------+   +------------+  |
| |                             |   |  inset /   |  |  <- 定位小图(只第一张)
| |                             |   |  locator   |  |
| |                             |   +------------+  |
| |         MAIN MAP            |         ^ N       |  <- 指北针(各图一致)
| |     (fuel classes)          |                   |
| |                             |   +------------+  |
| |                             |   |  Legend    |  |  <- 图例
| |                             |   |  ▢ pasture |  |
| |                             |   |  ▢ gorse   |  |
| |                             |   |  ▢ broadl. |  |
| |                             |   |  ▢ pine    |  |
| +-----------------------------+   +------------+  |
|                                   |__|__| 0 1km   |  <- 比例尺(条形)
| Source: Landsat 8 / LCDB · EPSG:2193 (NZTM)       |  <- 来源+投影
+---------------------------------------------------+
Figure X. ...(stand-alone caption，Figure X 加粗，放图下方)
```
右列从上到下：**inset → N → 图例 → 比例尺**，全部**左对齐**。

---

## 6. 好看的加分项（配色/细节）
- **语义配色**：pasture 浅黄绿、gorse/broom 黄橙(呼应开花)、broadleaf 深绿、pine 墨绿；refugia 图 unburned=绿、越烧越红。用 **ColorBrewer** 挑(定性/顺序/发散三类)，别自己乱调。
- **打印黑白也能分**：类别间明度拉开。
- **克制**：网格/经纬网能少则少，图面越干净越"贵"。
- **一致**：多张图共用**同一套边框、字体(跟报告一致 Calibri)、比例尺样式、指北针、AOI 范围** → 并排像一套的。

## 7. ArcGIS Pro 操作提示
- **View → Guides** 拉竖线，右列元素靠它 **Align Left**（顺手治"左边被裁"）。
- 选中元素 **Format → Arrange → Align Left** 批量对齐。
- 主图 frame 占左 ~⅔ 宽，右 ⅓ 竖排四个辅助元素。

## 8. 延伸阅读（真实来源）
- ESRI ArcGIS Pro 官方文档：*Add a legend / scale bar / north arrow to a layout*（最权威的操作参考）
- Cynthia Brewer, *Designing Better Maps: A Guide for GIS Users*（配色/排版经典，ColorBrewer 作者）
- Slocum et al., *Thematic Cartography and Geovisualization*（专题制图教材）
- ColorBrewer2.org（选色工具）
