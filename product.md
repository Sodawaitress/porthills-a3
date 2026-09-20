# A3 Product Backlog — 一次一块
> 这是**你的**作战面，每天打开这个。（`workflow.md` 是给 Claude 用的方法手册，你不用碰。）
> 截止 **2026-09-23** · 一次只做一块（WIP=1）· 做完把 🔲 改 ✅。

---

## 🔵 现在做：US8/US9/US10 — 流程图 + 地图 + 收尾

- ✅ US1-US7 全部完成！§3(20)+§4(25)+§5(27)=72分主体材料全部出图出数，report.md 对应段落都写好了。
- US6 最终结果：4类RF模型(排除bare_rock/cleared_pine，两者都改用已知/部分已知的掩膜)，**OA=0.684, Kappa=0.579**——历次版本里最诚实的数字，之前更高的分数是位置错误的cleared_pine撑出来的假象。
- US7 refugia 结果：**植被类型**——`exotic_pine`(21.4%)/`pasture`(19.9%)幸存率明显高于`broadleaf_scrub`(14.9%)/`gorse_broom`(14.0%)；**地形**——refugia比过火区高程更高(247.9m vs 219.2m)、坡度更缓(16.1° vs 17.5°)、更不朝北(0.13 vs 0.28)，三者都统计显著(p<1e-20)且符合火生态学常识。两条证据都支持"植被类型+地形跟refugia有关系"这个课题核心假设。

**下一步**（还剩的）：
- US8：更新流程图（10分，还没动）
- US9：正式地图出图（6要素）——分类图+refugia图已经有底稿(`FuelClass_4class_map_clipped`、`refugia_veg_terrain.png`)，缺正式排版
- US10：§2目的收尾 + §8时间线

→ US8流程图分最重，建议优先。

<!-- 做完把上面这块换成下一个 🔵，旧的勾到下面 backlog -->

---

## 协作 loop（每一块都走这 7 步）
`1 设计（我讲怎么做+为什么）→ 2 你确认 → 3 动手（脚本我写你读，决定你拍）→ 4 解释 → 5 你跑/看结果 → 6 你写那句英文 → 7 考核（我问2问）→ 下一块`

> 📄 **报告跟着走** → `report.md`（R1–R8）。每做完一个分析 US，loop 第 6 步就写它喂的那段 R，别攒到最后。

---

## US backlog（从 A2 proposal 落到 A3）

| US | 内容 | 产出 | 喂 | 状态 |
|---|---|---|---|---|
| US1 | 采训练/验证点（6 类） | labeled points，最终 211 个 | §5 | ✅ |
| US2 | 建特征栈 + 采样成点表 | `scripts/PortHills_PointTable.csv`，**211** 点×22波段 | §3–§5 地基 | ✅ |
| US3 | §3 数据探索（离群/正态/变换） | First pass + Second pass(正态性) + 变换测试，全部完成 | §3 (20) | ✅ |
| US4 | §4 关系（相关/散点 / dNBR 线性回归 / VIF） | 相关表+VIF清理+回归R²=0.41-0.48+散点图 | §4 (25) | ✅ |
| US5 | §5 可分性（JM + 光谱曲线） | JM矩阵+光谱曲线图，gorse/native最难分 | §5 | ✅ |
| US6 | §5 分类 RF + 混淆矩阵 | OA=0.71 Kappa=0.638，混淆矩阵+特征重要性图 | §5 (27) | ✅ |
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
| 1.4 | LCDB→**6**类 对照表 | 见下表，Manuka/Kanuka 按易燃性归 gorse_broom（不按 native）；新加 **cleared_pine**（exotic_pine 内非郁闭林冠区，含新鲜伐木迹地/林窗，按 Scott&Burgan 燃料模型惯例单列，见 workflow.md 方法记录） | ✅ |
| 1.5 | 分层布点 | **6 类共 252 点**，`TrainingPoints_raw`，70/30 空间分块 | ✅ |
| 1.6 | 抽验/修正标签 | bare-rock 补了 15 点；坡向核查+补点(exotic_pine 背阳+10)；exotic_pine 删了 3 个误落采伐迹地的点、留了 1 个真是年轻松树的 | ✅ |
| 1.7 | 导出 → 上传 GEE asset | 属性已有 `class_id`（整数）→ 喂 US2 | 🔲 |

**1.4 的对照表（已定）**：

| LCDB 原始类 | → FuelClass |
|---|---|
| Gorse and/or Broom、Manuka and/or Kanuka | gorse_broom |
| Exotic Forest | exotic_pine |
| High/Low Producing Grassland、Orchard/Vineyard、Short-rotation Cropland | pasture |
| Broadleaved Indigenous Hardwoods、Indigenous Forest | broadleaf_scrub |
| Built-up Area | 排除（AOI 内只 0.05ha，可忽略） |
| （bare-rock） | LCDB 没有对应类，US1.6 补 |
| Exotic Forest 内的非郁闭区（亮度高+绿度低，去噪后 ~25ha，占 exotic_pine 6.6%） | **cleared_pine**（新第 6 类，US1.6 加） |

> ⚠️ 1.2 的坑：判读底图**得是 2017 火前**的，别用火后图（标签会和火前特征栈对不上）。

---

## 🟡 2017 改进候补（下一步 · 先把2024做完看效果再回来挑）

> 2024复现过程中读文献/踩坑找到的新方法，原则上两次项目都该用；但**现在先不动2017**，
> 等2024这条线跑出效果、验证过是真有用，再回来把适用的搬回2017的report.md/workflow.md。
> 这里先把"找到了什么、哪条真的适合2017、值不值得搬"记清楚，别丢。

| # | 候选 | 出处 | 已验证？ | 适合2017吗 |
|---|---|---|---|---|
| F1 | Spearman秩相关跟Pearson并排跑 | references.md E3 Domingo2020 | ✅已在2017点表上跑过(`scripts/04e_spearman_correlation.py`)：n=186，**排序真的变了**——`pre_B4`从Pearson显著(p=0.004)变Spearman不显著(p=0.069)，跟§3已发现的"19/72组非正态"互相印证 | ✅适合，是真结果不是空谈，§4现成能用 |
| F2 | "每个变量单独出图"当§3探索方法的引用背书 | references.md E2 Solares2023 | 方法本身2017已经在做(boxplot/hist逐变量) | ✅适合，纯补引用零成本 |
| F3 | Gini重要性引用 + 可选drop-one法 | E2 Solares / E3 Domingo | Gini重要性2017已隐式在用(sklearn默认)；drop-one没做过 | ✅引用部分适合；drop-one算新分析，值不值得看时间 |
| F4 | RF过拟合反例对照(Domingo拟合0.99/验证0.56 vs 本研究OOB0.627/验证0.71) | E3 Domingo2020 | 数字都现成(2017 US6已有) | ✅适合，纯讲故事素材 |
| F5 | skew/kurt当标准描述量的引用背书 | E2 Solares2023 Table3 | 方法2017已在用 | ✅适合，纯补引用 |
| F6 | 多时相/物候分gorse↔broadleaf(JM=1.46最弱对) | E2/E3 | 没做过，真新分析 | ⚠️属于A4范围，2017本身没有S2物候时序数据 |
| — | Coppoletta(2016)重烧机制 | references.md A6 | 已核实 | ⚠️主要讲"重烧"，2017不是重烧事件，更适合2024自己的故事，不强搬 |

**下一步**：2024那条线（§3-§5等效）先跑完看结果，回头再从这张表挑，挑完了才动
report.md的§3/§4正文（英文句子还是你写）。

---

## 记着（到时别忘）

**US8 更新流程图要加的 4 个框**（改 `refine/fig_workflow.dot`，插在"特征栈→分类"之间）：
1. 点表节点　2. §3 数据探索框（离群 IQR→正态 skew/kurt→变换）　3. §4 关系框（相关/散点→回归→VIF）　4. terrain 多引一条线进"探索+关系"
（到 US8 再画——§6 要的是"实际做了什么"，得等 US3/US4/US6 跑完。）
