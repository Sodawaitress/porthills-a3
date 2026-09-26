# 地图排版笔记 · 老师反馈 + 最好看的做法（A4 重做地图照这个）

> 学习/规划笔记，非提交正文。服务 A4 的 Map1(燃料分类)、Map2(refugia)、Fig5_8。
> 更新：2026-09-26

---

## 1. 老师原话反馈（verbatim，A3 地图批注）

> "For future, I would move the **main map to the left** of your figure, and place the **insert map, legend and scale bar all on the right** of your map along with the **N arrow**. Be careful that you have **slightly cut off the left of the insert map, legend and scale bar**."

拆成两条 actionable：
1. **重排**：主图挪到左边(占最大块) → 右侧竖排放 inset(定位小图)、N 指北针、图例、比例尺。
2. **修 bug**：inset / 图例 / 比例尺的**左边被裁掉了一点** → 布局时留够页边距，别贴边。

---

## 2. 为什么这样排最好看（原理，不是背规则）

- **视觉层级**：主图是主角，读者视线从左上进入 → 主图放左边、给最大空间，一眼落在它上面；辅助元素(inset/图例/比例尺/指北针)是配角，**全部收到右边一列**，不跟主图抢注意力。
- **分组 = 干净**：同类东西聚在一起(右列全是"读图工具")，比零散撒在四角更整齐、留白更规整。
- **对齐**：右列元素**左边缘对齐**成一条隐形竖线(ArcGIS Pro 里用 Guides 拉一条参考线,所有元素吸附上去) → 这也顺手根治老师说的"左边被裁"问题。
- **留白/页边距**：布局四周留 ≥0.5–1cm 白边，任何元素都别碰到图框边——"被裁掉"就是元素放到了出血区外。

---

## 3. 推荐布局（ASCII 草图，A4 照着摆）

```
+---------------------------------------------------+
| Map 1 — Pre-fire fuel classes, Port Hills 2017    |  <- 标题(左上或顶部)
| +-----------------------------+   +------------+  |
| |                             |   |  inset /   |  |  <- 定位小图(NZ/Canterbury
| |                             |   |  locator   |  |     里圈出 AOI)
| |                             |   +------------+  |
| |         MAIN MAP            |         ^ N       |  <- 指北针
| |     (fuel classes)          |                   |
| |                             |   +------------+  |
| |                             |   |  Legend    |  |  <- 图例(4类颜色块)
| |                             |   |  ▢ pasture |  |
| |                             |   |  ▢ gorse   |  |
| |                             |   |  ▢ broadl. |  |
| |                             |   |  ▢ pine    |  |
| +-----------------------------+   +------------+  |
|                                   |___|___| 0 1km |  <- 比例尺
| Source: Landsat 8 / LCDB · EPSG:2193 (NZTM)       |  <- 来源+投影(底部)
+---------------------------------------------------+
```
右列从上到下：**inset → N 指北针 → 图例 → 比例尺**，全部**左对齐**成一条线。

---

## 4. 一张好地图的必备元素（你 report.md R7 已在查的 6 项 + 补充）

| 元素 | 要点 |
|---|---|
| **标题 Title** | 说清"什么变量 + 哪里 + 什么时间"(如 "Pre-fire fuel classes, Port Hills, 2017") |
| **图例 Legend** | 4 类颜色块 + 文字；颜色要能区分、对色盲友好(避免红绿并列) |
| **比例尺 Scale bar** | 用**条形比例尺**(不用"1:xxxxx"文字比例，缩放打印会失真) |
| **指北针 North arrow** | 简洁即可，别用花哨的；NZTM 下正北 |
| **定位小图 Inset/Locator** | 在大范围(NZ 或 Canterbury)里圈出 AOI，读者才知道在哪 |
| **来源 + 投影 Source + CRS** | 底部小字：数据源(Landsat 8 / LCDB) + **EPSG:2193 (NZTM)** |
| 补：**图框/邻域** | 主图外可留浅色底图/等高线做上下文，但别喧宾夺主 |
| 补：**字体统一** | 全图一种字体(跟报告一致用 Calibri)，字号分级(标题>图例>来源) |

## 5. "更好看"的加分项（配色/细节）

- **配色**：燃料 4 类用**语义色**——pasture 浅黄绿、gorse/broom 黄橙(呼应开花)、broadleaf 深绿、pine 墨绿；refugia 图 unburned=绿、越烧越红。用 ColorBrewer 的定性/顺序色板挑，别自己乱调。
- **对比**：类别之间明度/色相拉开，打印黑白也能分。
- **克制**：网格线、经纬网可选；能少则少，图面越干净越"贵"。
- **一致**：Map1 和 Map2 用**同一套边框、字体、比例尺样式、AOI 范围** → 两张并排像一套的。

## 6. ArcGIS Pro 里怎么落地（操作提示）

- Layout 里 **View → Guides** 拉竖/横参考线，右列元素靠参考线**左对齐**(直接修掉"左边被裁")。
- 元素选中后 **Format → Arrange → Align Left** 批量对齐。
- 主图 frame 拉大占左 ~⅔ 宽；右 ⅓ 竖排放四个辅助元素。
- 导出 **File → Export Layout**，四周留白，别导出到贴边。

## 7. 延伸阅读（真实来源，想深入再看）

- ESRI ArcGIS Pro 官方文档：*Add and modify a legend / scale bar / north arrow*（Layout 排版最权威的操作参考）
- Cynthia Brewer, *Designing Better Maps: A Guide for GIS Users*（配色/排版经典，ColorBrewer 作者）
- Slocum et al., *Thematic Cartography and Geovisualization*（专题制图教材，视觉层级/图面组织）
- ColorBrewer2.org（选色工具，定性/顺序/发散三类色板）
