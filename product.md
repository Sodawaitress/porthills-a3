# A3 Product Backlog — 一次一块
> 这是**你的**作战面，每天打开这个。（`workflow.md` 是给 Claude 用的方法手册，你不用碰。）
> 截止 **2026-09-23** · 一次只做一块（WIP=1）· 做完把 🔲 改 ✅。

---

## 🔵 现在做：US1.6/1.7 — 补 bare-rock + 导出点表

- ✅ k-means 诊断跑完 → `A3/kmeans_diagnostic/`。
- ✅ LCDB 已裁到 AOI（`lcdbPorthills`，121 个多边形），按 `Class_2012` 定了 `FuelClass` 字段（对照表见下 US1.4 行）。
- ✅ 分层撒点：4 类 × 50 = 200 点，`TrainingPoints_raw`，70/30 分（空间分块避免自相关，见下）。
- ✅ ArcGIS Pro 工程搬到 `Desktop\PortHills\`（不再嵌在 `a3\` 里），OneDrive 留一份备份。

**下一步**（二选一）：
1. bare-rock 还没点——LCDB 里没有对应类，得靠 2015 航片目视核对补几个点。
2. 或者先跳过 bare-rock，把现有 200 点在特征栈上采样出点表（US2 地基），bare-rock 点补齐了再并进去。

→ 你定先做哪个，我接着写脚本。

<!-- 做完把上面这块换成下一个 🔵，旧的勾到下面 backlog -->

---

## 协作 loop（每一块都走这 7 步）
`1 设计（我讲怎么做+为什么）→ 2 你确认 → 3 动手（脚本我写你读，决定你拍）→ 4 解释 → 5 你跑/看结果 → 6 你写那句英文 → 7 考核（我问2问）→ 下一块`

> 📄 **报告跟着走** → `report.md`（R1–R8）。每做完一个分析 US，loop 第 6 步就写它喂的那段 R，别攒到最后。

---

## US backlog（从 A2 proposal 落到 A3）

| US | 内容 | 产出 | 喂 | 状态 |
|---|---|---|---|---|
| **US1** | 采训练/验证点（5 类） | labeled points | §5 | 🔵 进行中 |
| US2 | 建特征栈 + 采样成点表（GEE） | CSV 点表 | §3–§5 地基 | 🔲 脚本已草 |
| US3 | §3 数据探索（离群/正态/变换） | 图 + 结论 | §3 (20) | 🔲 |
| US4 | §4 关系（相关/散点 / dNBR 线性回归 / VIF） | 表 + 结果 | §4 (25) | 🔲 |
| US5 | §5 可分性（JM + 光谱曲线） | 图 | §5 | 🔲 |
| US6 | §5 分类 RF + 混淆矩阵 + AlphaEarth 对比 | 分类图 + 矩阵 | §5 (27) | 🔲 |
| US7 | §5 refugia 支线（S2 dNBR） | refugia 图 | §5 | 🔲 |
| US8 | §6 流程图更新 | 流程图 | §6 (10) | 🔲 |
| US9 | §7 地图 | 地图 | §7 (4) | 🔲 |
| US10 | §2 目的收尾 + §8 时间线 | 文字 + 表 | §2/§8 (9) | 🔲 |

---

## US1 展开（最小块 · 我推荐了默认，你改）

| # | 小块 | 我的推荐（你可改） | 状态 |
|---|---|---|---|
| 1.1 | 定 5 类 + 每类点数（k-means 诊断验证） | 诊断已跑，4 类对上 LCDB | ✅ |
| 1.2 | 定判读底图（**必须火前**） | Route B：LCDB `Class_2012` 当种子 + 2015 航片核验 | ✅ |
| 1.3 | 建工作台 | LCDB 裁到 AOI，进了 ArcGIS Pro 工程 gdb（`lcdbPorthills`） | ✅ |
| 1.4 | LCDB→5类 对照表 | 见下表，Manuka/Kanuka 按易燃性归 gorse_broom（不按 native） | ✅ |
| 1.5 | 分层布点 | 4 类 × 50 = 200 点，`TrainingPoints_raw`，70/30 空间分块 | 🟡（缺 bare-rock） |
| 1.6 | 抽验/修正标签 | 高分影像上核一批，改错标 + 补 bare-rock | 🔲 |
| 1.7 | 导出 → 上传 GEE asset | 属性已有 `class_id`（整数）→ 喂 US2 | 🔲 |

**1.4 的对照表（已定）**：

| LCDB 原始类 | → FuelClass |
|---|---|
| Gorse and/or Broom、Manuka and/or Kanuka | gorse_broom |
| Exotic Forest | exotic_pine |
| High/Low Producing Grassland、Orchard/Vineyard、Short-rotation Cropland | pasture |
| Broadleaved Indigenous Hardwoods、Indigenous Forest | native_scrub |
| Built-up Area | 排除（AOI 内只 0.05ha，可忽略） |
| （bare-rock） | LCDB 没有对应类，US1.6 补 |

> ⚠️ 1.2 的坑：判读底图**得是 2017 火前**的，别用火后图（标签会和火前特征栈对不上）。

---

## 记着（到时别忘）

**US8 更新流程图要加的 4 个框**（改 `refine/fig_workflow.dot`，插在"特征栈→分类"之间）：
1. 点表节点　2. §3 数据探索框（离群 IQR→正态 skew/kurt→变换）　3. §4 关系框（相关/散点→回归→VIF）　4. terrain 多引一条线进"探索+关系"
（到 US8 再画——§6 要的是"实际做了什么"，得等 US3/US4/US6 跑完。）
