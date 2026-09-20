# A3 Product Backlog — 一次一块
> 这是**你的**作战面，每天打开这个。（`workflow.md` 是给 Claude 用的方法手册，你不用碰。）
> 截止 **2026-09-23** · 一次只做一块（WIP=1）· 做完把 🔲 改 ✅。

---

## 🔵 现在做：US7/US9 — refugia 支线 + 地图

- ✅ US1-US6 全部完成！§3(20)+§4(25)+§5(27)=72分主体材料全部出图出数，report.md 对应段落都写好了。
- US6 最终结果：`cleared_pine`原来28个训练点里26个位置查出来是错的(不在exotic_pine范围内)，重新采点后只剩19个真正正确的点，分3-4个小图斑——太少太集中，分类器学不出边界(PA=0.067)。跟`bare_rock`(7点，无完整边界)一样处理：都从RF训练集剔除，改用掩膜——`cleared_pine`有真实边界(`cleared_pine_real`)可以直接用，`bare_rock`仍是已知空白。**最终4类模型：OA=0.684, Kappa=0.579**（比中间几个版本都低，但那些高分都是位置错误的cleared_pine撑出来的假象，这个是诚实数字）。`broadleaf_scrub`↔`gorse_broom`混淆是这两类本身光谱重叠的真实限制。
- US4 补充：测过 RF 回归代替线性回归，全6类时结果更差（验证集R²=0.371 vs 线性0.413/0.476）；⚠️ 之前引用的"256-512样本量门槛"数字查不到出处已撤回（Yu核实+我试了4个来源都打不开原文），改成自己测：只用4个大类(排除bare_rock/cleared_pine)对比176点vs256点，线性R²始终很差(-0.157→0.047)，**RF明显随样本量改善(0.105→0.403)**，这个自测证据比外部引用更直接。另查了2015年火前LiDAR算冠层高度(CHM)，覆盖有缺口不能进正式模型，降级为170点的补充描述性证据(exotic_pine冠层最高但dNBR不是最高，支持"燃料类型比生物量更决定烧毁结果")。

**下一步**（还剩的）：
- US7：refugia 支线（哪些地方没烧、用分类图+燃烧结果叠一叠）
- US8：更新流程图（10分，还没动）
- US9：正式地图出图（6要素）
- US10：§2目的收尾 + §8时间线

→ 这几个哪个先做你定，US8流程图分最重，建议优先。

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

## 记着（到时别忘）

**US8 更新流程图要加的 4 个框**（改 `refine/fig_workflow.dot`，插在"特征栈→分类"之间）：
1. 点表节点　2. §3 数据探索框（离群 IQR→正态 skew/kurt→变换）　3. §4 关系框（相关/散点→回归→VIF）　4. terrain 多引一条线进"探索+关系"
（到 US8 再画——§6 要的是"实际做了什么"，得等 US3/US4/US6 跑完。）
