# ERST619 A3 — Preliminary Analysis Workflow
Kaupapa Tuhika 3 · Lincoln University · S2 2026
截止：**2026-09-23（周三）23:59 · Learn 提交** · 权重 **20%** · 一个 PDF · ~2000 词 / 5–10 页正文（附录不计）

> ⚠️ **非提交**。**这份 `workflow.md` = 给 Claude 用的方法/参考手册**；**`product.md` = Yu 的作战面（US 待办）**。
> 这里是骨架、料、决定点。

---

## A3 是什么（A2 → A3 的转变，先搞懂这个再动手）

| | A2（提案，已交） | **A3（现在）** |
|---|---|---|
| 动词 | "I **will**…"（计划） | "I **did**… 结果是… 这里**有问题**… 这样改"（做了+**评估**） |
| 采分词 | proposal | **preliminary · evaluation**（初步·自评） |
| 新增的层 | — | **统计数据探索**（离群值·正态性·变换）+ **回归** + **真跑一遍分类并报精度** |
| Helen 要看的 | 你的计划 | 每步都凑齐 **①做了什么 ②为什么 ③局限**（A1 丢分就丢在②③没说） |

一句话：**A3 = A2 那张流程图，加上"真执行 Wegmann 第2–8步 + 统计探索层"**。

---

## 分数地图（marks 在哪，先看这张再分配精力）

| 报告节 | 内容 | 分 | 状态 |
|---|---|---|---|
| 1 封面 | 标题 + 姓名 + 学号 | 0 | 🔲 |
| 2 目的 | Wegmann Step 1：为什么要分类图 + 怎么用 | 5 | 🔲 |
| 3 数据探索 | 清洗5 · 离群值5 · 正态性5 · 变换5 | **20** | 🔲 |
| 4 关系 | 相关表5 · 散点5 · 哪种回归5 · 回归结果5 · 精度评论5 | **25** | 🔲 |
| 5 分类 | 训/验数据5 · 可分性5 · 光谱可分性5 · 像元/对象2 · 算法5 · 结果5 · 精度评论5 | **27** | 🔲 |
| 6 流程图 | 更新版流程图 + way forward | **10** | 🔲 |
| 7 地图 | 高质量地图（A1/A2 标准） | 4 | 🔲 |
| 8 时间线 | 更新到 A4 + 口试 | 4 | 🔲 |

→ §3+§4+§5 = **72分是统计中身**。光流程图 10分。**精力照这个比例放。**

---

## 数据清单（一切下游的输入 · 沿用 A2 的决定）

**Image variables（影像变量）**
| 类别 | 具体 | 状态 |
|---|---|---|
| 光谱波段 | Landsat 8 C2L2 火前 SR_B2–B7（6 波段）⚠️缩放 ×0.0000275 − 0.2 | 🔲 |
| 指数 | NDVI · NDWI · BSI · NDRE(仅S2) · dNDVI · NBR/dNBR | 🔲 |
| Ancillary（地形 correlates） | DEM → elevation · slope · aspect · TWI · TCI · TRI · solar irradiation | 🔲 |

**"Field data"（实地数据 = 高分参考影像判读点，你没野外点）**
| 项 | 具体 | 状态 |
|---|---|---|
| 类别标签 | 从 LCDB v4.1 + 航拍/高分影像目视判读的点 | 🔲 |
| 分类体系（A2 定 5 类，A3 期间扩到 6 类） | pasture / gorse-broom(高易燃) / exotic pine / native scrub(低易燃) / bare-rock / **cleared_pine**(新加，见下方法记录) | ✅ 6 类都有点了 |

⚠️ 课题原文点名："field data ... sometimes collected off **'reference imagery'** where field data are not available" —— 就是你这种情况，**光明正大用高分影像取点**，说清楚即可。

---

## ⭐ 核心数据结构：训练/验证点表（两份 lab 的隐藏主线）

两份 lab 指向同一个数据结构：**一张点表**。
- 每行 = 一个从参考影像判读的点；列 = **类别标签 + 各波段值 + 各指数值 + 各地形值**（在该像元采样）。
- §3 统计探索、§4 关系/回归、§5 分类 —— **全跑在这张点表上，不是整幅栅格**。
- L8 明说：ArcPro 要先 **Raster to Point**（把栅格在点位上取值）；R/Python 可直接在栅格上做。
- **所以第一件大事** = 把 6 波段 + 指数 + 地形栈，在训练/验证点上采样，导成一张属性表。**这张表是 §3–§5 的地基。**

## 软件：lab 教的 vs 你会的（decision #5 现在有据了）

- **lab 全程用 ArcGIS Pro** 演示：Data Engineering（算 skew/kurtosis/直方图）、Select By Attributes（按 IQR 删离群）、Transform Field、散点矩阵、相关表、Generalized Linear Regression、VIF；Georef lab 教配准+数字化。
- 但 Helen 片子里**两次明说**：变换/正态"**probably more easily handled in R or Python，Arc 很慢**"；"R/Python 里可直接在栅格上做"。→ **用 Python/GEE 做统计完全正当、往往更快。**
- ⚠️ A3 原文："based on feedback received in **Labs**" → 至少要**对得上 lab 的流程和术语**（IQR fences、skew>\|1\|、kurt>\|2\|、VIF、RMSE/R²）。
- **务实分工（建议，你定）**：

| 环节 | 用什么 | 为什么 |
|---|---|---|
| 采点/数字化训练数据 + 配准航片 | **ArcPro** | Georef lab 就教这个；LCDB/航片在 Arc 里顺手 |
| §3/§4 统计（离群/正态/变换/回归） | **Python / GEE** | Helen 说 Arc 慢、R/Python 更好；在家做避机房 |
| 分类 + 混淆矩阵 | **GEE**（或 ArcPro） | RF + 混淆矩阵自带 |
| 最终地图 | **ArcPro** | 制图排版强 |

⚠️ 不管用哪个，**术语和图对齐 lab**（这样才吃"based on Labs"那句）。

---

## 协作 loop（我 Claude 怎么和 Yu 干活 · 照她 COMP639 "每次必须遵守"）

1. **设计** — 我讲这个 US/块 怎么做、为什么
2. **她确认** — 她说"可以"我才动手（不自己冲）
3. **动手** — 脚本我写、她读；决定她拍
4. **解释** — 讲不看代码看不出的点
5. **她跑 / 看结果**
6. **她写那句报告英文**（她的声音）
7. **考核** — 我问 2 个问题，确认她真懂 → 下一块

> 📁 **US backlog + 每个 US 的最小块 + 状态 → 全在 `product.md`**（那是 Yu 的作战面）。
> 这份 `workflow.md` 是**给我 Claude 用的**方法/参考手册，别把 US 待办再抄回这里（一处真相）。

---

## 管线（core · 每块标状态 · 挂 rubric · 标"你要定"）

### 阶段 0 — 目的（§2, 5分）🔲
- **做什么**：Wegmann Step 1。为什么要一张**植被/燃料分类图** + 你会拿它干嘛。
- **为什么**：给整篇定调；Helen A1 说过每个论断挂引用。
- **料**：直接搬 A2 的 why 链（暖化→Canterbury 火险→gorse 清林遗产→Wyse lab/field 缺口）。见 `Fire_Assessment_2026/A2_提案/A2_提案骨架_非提交.md` §2。
- **你写**：120–150 词，压缩 A2 那 5 拍。

### 阶段 1 — 组数据 + 空间清洗（§3 第1项, 5分）🔲
- **做什么**：缩放到反射率、云/影掩膜、median 合成、裁到 AOI、重投影 NZTM(EPSG:2193)、去 no-data。
- **为什么**（逐条一句）：⚠️没缩放全错（120 offset 的教训）；云污染当离群值/坏样本；裁 AOI 省算力+聚焦；NZTM 量算才准。
- **喂**：§3 "spatial data cleaning + why"。
- **状态**：A1 脚本已有大半（6 波段 + 22 层 stack），复用改造。

### 阶段 2 — 数据探索：两遍过（§3 后3项, 15分）🔲 ← L8 讲座的核心配方
L8 把它拆成 **First pass（清离群/空值）** 和 **Second pass（正态/变换）**，全在点表的每一列上做。每步都要 **出图 + 下结论 + 给理由**。

**First pass — 离群值 + 空值（喂 "outliers" 5分）**
- **空间离群**：地图上看，非目标区 / 受其他因素影响的 → 数字化 mask 多边形裁掉。
- **属性离群**：每列画 **boxplot**，用 **IQR fences** 判：
  - 下界 `Q1 − 1.5×IQR`，上界 `Q3 + 1.5×IQR`（超出 = 离群）。
  - ArcPro：Select By Attributes 写 `B8 > (Q3 + 1.5*IQR)` 选出→删；Python 同理。
  - **顺序**：从最严重的列开始 → 删 → 重算箱线 → 其他列改善没？（L8 原话 "The hours I could have saved!!!"）
- **判 error 还是 signal**（决定 keep/delete = 拿分关键）：
  - **Global outlier**（整体离群）→ 通常 remove。
  - **Contextual/conditional**（如"夏天却像冬天"的季节异常）→ 判断，未必删。
  - Collective outlier → 难，lab 不要求。
- **空值 Nulls**：排序+查询选出 → delete（<5% 均值/众数补；5–20% KNN/多重插补；>20% 慎用）。**常数列**（只一个值）无预测力 → 删。**重复行** → 删（会 bias）。
- ⚠️ **L8 教学彩蛋**："Oops! Perhaps this is not an outlier issue, but **normality**" —— 别把"分布偏"当"离群"猛删；有时该做的是**变换**，不是删点。这句写进报告 = 显示你懂分寸（正中 Helen 靶心）。

**Second pass — 正态性 + 变换（喂 "normality" 5 + "transformation" 5）**
- **正态性**：每列 **histogram + skewness + kurtosis**。
  - 判据（lab 给的线）：**skewness < −1 或 > 1 = 非正态**；**kurtosis < −2 或 > 2 = 非正态**。
  - ArcPro：Analysis > Data Engineering > 属性表算 skew/kurt/直方图一次出。Python：`scipy.stats.skew / kurtosis`。
  - ⚠️ **点明**：RF **不要求正态**；但回归、部分可分性度量要 → 正态性主要服务 §4 回归。
- **变换**（测哪个 · 为什么 · 改善没；不做也 justify）：

  | 变换 | 适用 | 坑 |
  |---|---|---|
  | Min/Max | 缩到固定区间、保形；**可视化用** | 对离群极敏感；**分析不推荐** |
  | **Log** | **右偏**数据 | 不能用于 ≤0；难解释 |
  | Sqrt / Z-score | 让高量级变量不主导 | 扭曲原单位；对极端离群敏感 |
  | Box-Cox | 强制近正态 | 只 >0；要估 λ 参数 |
  | Robust / IQR scaling | 用中位数+IQR | 抗重离群；无固定区间 |

  - L8 结论："**some better, some worse — take your time, get advice**"（Helen 让你找 LU 统计支持）。
  - ArcPro：Data Engineering > Construct > **Transform Field**（很慢、字段名 ≤10 字符、别放 OneDrive）；R/Python 更顺。
  - **标准化**（把各波段放同一尺度）：Z-score 用于分析；Min/Max **只用于可视化**（lab 明说 "not recommended for analysis"）。
  - ⚠️ RF 尺度不变 → 若你只用 RF，标准化对**分类**可能没必要；但你**必须调查过 + 写明**才拿这 5 分（"不做也要 justify why"）。
- **你要定 #1**：哪些变量进这套探索？（建议：6 波段 + 主要指数 + 地形层，全过一遍）
- ⚠️ L8 总结原话："The process is **not once-off** and always requires exploration and repetition." + "**Seek statistical advice**"（两次）→ 报告里体现"我试了几轮"就是分。

### 阶段 3 — 关系：影像 ↔ 实地变量（§4, 25分）🔲 ← L8 后半 + Helen 强推 ArcPro 回归文档
全在点表上做。⚠️ **你的 field 变量是类别型**，走法和 lab 的连续例子（谷物产量）**不完全一样** → 见 decision #2。

| 步 | 做什么 | 关键 | 分 |
|---|---|---|---|
| 3a 相关表 / cross-tab | **数值↔数值**（如 dNBR vs 波段）：相关表，报 **correlation · n · p-value** 并排序；**类别↔数值**：**Cross Tabulation**（L8 明说"usually categorical"、"≈ 混淆矩阵"）——给你植被类的路 | 找冗余/有信息量的预测变量 | 5 |
| 3b 散点矩阵 | ArcPro Chart 散点矩阵；开 trend line + 显示 R²/p；看形状、找离群 | 目视关系形状 | 5 |
| 3c 哪种回归 + 为什么 | 见 decision #2。类型（L8）：**Linear ŷ=a+bx**（恒定变化率）/ Exponential / Logarithmic / No correlation；类别响应→**Logistic** | 选择+论证本身就是分 | 5 |
| 3d 回归结果 + 解读 + 挂3文献 | 报系数（intercept a、slope b）+ 评估指标；最佳拟合 = 最小化 Σ(y−ŷ)² | 把数字讲成故事 | 5 |
| 3e 精度评论 | 多准、什么问题、怎么改 | "evaluation" 的核心动词 | 5 |

**回归评估指标（L8，报告要用）**：
- **MAE** = 平均绝对误差（同单位、好懂："平均差 X"）
- **MSE** = 均方误差（罚大误差，非原单位）
- **RMSE** = 均方根误差（同单位、**越小越好**，L8 高亮）
- **R²** = 决定系数（模型解释了 Y 多少方差）

⭐ **多重共线性（L8 专门一页，别漏——你波段+指数高度相关）**：
- 相关 **>0.8–0.9** → 拿掉其中一个再回归。
- **VIF**：<5 安全；5–7.5 谨慎；**>7.5 冗余 → 删 VIF 最高的重跑**。
- 影响线性和逻辑回归；系数会不稳、难解释。

**你要定 #2（这块最拧巴，现在有据了）**：field 是**类别型**。两条都正当，选一个、报告里说清为什么：
- **A（推荐）**：造连续目标——用 **dNBR 燃烧强度**当 Y，跑**线性回归**（预测变量=火前波段/指数/地形）。① 完全对齐 lab 的连续例子；② 直接服务你的 refugia 科学问题（"火前植被/地形能否预测烧得多重/烧不烧"）；③ 自然出 R²/RMSE。
- **B**：保持类别 → **逻辑回归**（烧/未烧，或某类 vs 其余）+ **Cross-tab**。lab 明确支持 cross-tab，多重共线性页也点名 logistic。
- 拿不准 → 问 Helen（她两次说 "seek statistical advice"；LU 有统计支持）。

**料**：Helen **强推 ArcPro 回归文档** `pro.arcgis.com/.../regression-analysis-basics.htm`；ArcPro 工具 = **Generalized Linear Regression (GLR)**。挂文献用 `Fire_Assessment_2026/notes_非提交/文献总表_非提交.md`（Meddens2018/Krawchuk2016/Wyse2016/Christ2025）。

### 阶段 4 — 分类（§5, 27分）🔲
| 步 | 做什么 | 为什么 | 分 |
|---|---|---|---|
| 4a 训/验数据 | 说清收了什么点、怎么收（参考影像判读）、多少、怎么分 | 数据决定上限 | 5 |
| 4b 类别可分性 | 各变量上类别分不分得开 | 分不开→合并类 | 5 |
| 4c 光谱可分性 | 训/验点对应像元的**光谱曲线** + **Jeffries-Matusita (JM)** 指数(→2 越可分) | 双峰=混了两类；引 Richards 2013 | 5 |
| 4d 像元 vs 对象 + 为什么 | 说用哪种+一句理由（A2 倾向像元 RF；对象法减椒盐噪声） | | 2 |
| 4e 算法 + 为什么 + 引用 | **Random Forest** + 为什么 RF 不用 DL（少样本、可解释、给变量重要性；Christ2025 也用 RF） | 分寸得当=加分 | 5 |
| 4f 结果+解读 / 精度评论 | 跑出初步分类图、解读、**混淆矩阵**(OA/Kappa/PA/UA)、问题+改法、挂文献 | | 5+5 |
- **训练/验证数据怎么来（Georef lab 就是教这个）**：
  - 把航片/高分影像**配准到 NZTM**：加控制点（点在影像→点在已知位置）→ 看 **Residual 越小越好** → 试 2nd/3rd order 变换 → 导出 **TIFF**（**bilinear** 重采样，带 world file `.tfw`）。
  - 在配准好的底图上**数字化植被**：新建 `VegType` 多边形要素类 → Create Features 描边（或点）→ 每个要素填类别 → 导出 **shapefile**（记住 shapefile 是一组文件 .shp/.shx/.dbf/.prj… 缺一不可）。
  - → 这就是你"从参考影像取的点/面"= 训练/验证数据。
  - 采样：把特征栈在这些点上取值（**Raster to Point** / sample）→ 得核心点表（见上"核心数据结构"）。
- **料**：训/验、可分性、精度全套在 A2 §5 已规划，见 `A2_提案骨架_非提交.md` §5 + `图像分类学习笔记.md` 步骤7/8/10。
- **你要定 #3**：训/验怎么分？（A2 提过：70/30 或按面积比例 area-proportional；未烧类少→过采样；空间块划分避免自相关）

### 阶段 5 — 更新流程图（§6, 10分）🔲
- **做什么**：把 A2 那张**计划图**改成**"我实际做了什么"图** + 加统计探索层 + 写 way forward（往 A4 最终分类+精度评估走）。
- **料**：现成 `refine/fig_workflow.dot`（最新最详版）和 `Fire_Assessment_2026/figures/fig_workflow.gv`。改这个，别从零画。
- **要加的新框**：数据探索层（清洗→离群值→正态性→变换）、关系/回归层、真·精度评估（混淆矩阵）。
- ⚠️ 10分单块最大的一格，别糊弄。工具：改 .dot 用 graphviz，或 draw.io。

### 阶段 6 — 地图（§7, 4分）🔲
- **做什么**：高质量**初步分类图** + burn/refugia 图。
- **6 要素每图查**：title / legend / scale bar / north arrow / inset(locator) / source+projection(EPSG:2193)。缺的在图底写理由。
- **料**：A1 的 dNBR/severity PNG 已达标，套同样制图标准。

### 阶段 7 — 时间线（§8, 4分）🔲
- **做什么**：更新到 **A4 最终报告 + 口试**，每周做什么。
- **料**：搬 A2 时间线往后延。

---

## 关键决定快查（只有你能定的，别让我替你编）

| # | 决定 | 选项 / 参考 | 状态 |
|---|---|---|---|
| 1 | 哪些变量进数据探索 | 6波段 + 主指数 + 地形层 | 🔲 |
| 2 | **哪种回归**（field 是类别型） | **A(推荐)** dNBR 当连续 Y→线性回归（对齐 lab+服务科学+出 R²/RMSE）；**B** 保持类别→逻辑回归+cross-tab。选一个说清为什么，拿不准问 Helen | 🔲 |
| 3 | 训/验怎么分 | **定了**：70/30，按 300m 空间格子整块分配（不逐点随机，避免自相关），见下"方法记录" | ✅ |
| 4 | 像元 vs 对象 | A2 倾向像元 RF | 🔲 |
| 5 | 软件 | **务实分工**：采点/数字化+配准=ArcPro；§3/§4统计=Python/GEE（术语对齐 lab）；分类+混淆矩阵=GEE；最终地图=ArcPro。见上"软件"节 | 🔲 |

---

## 技术处理快查（别再踩的坑）

| 项 | 值 |
|---|---|
| Landsat C2L2 缩放 | `SR × 0.0000275 − 0.2`（漏了全错） |
| Sentinel-2 缩放 | `/10000` |
| NBR | `(NIR − SWIR2)/(NIR + SWIR2)` |
| dNBR | `preNBR − postNBR`；异质地表出 RBR |
| 投影 | EPSG:2193 (NZTM) 量算/制图 |
| 2017 火 | 2017-02-13 起，官方 ~1661 ha；边界 shp 已在 `data/2017_fire_boundary_shp/` |
| 指数引用 | NDVI→Rouse1974；NBR/dNBR→Key&Benson2006；NDWI→McFeeters1996 |
| 火前必须用火前影像 | 烧掉处看不到原植被；2017-02 火前 S2 SR 还没有，只能 L8 |

---

## 方法记录 · US1.1 类别诊断（k-means）

- **脚本**：`A3/scripts/kmeans_class_diagnostic.py` —— 火前光谱(`pre_B2–B7 + NDVI + BSI`)，z-score 标准化，跑 k=5/6/7。
- **输入**：`refine/PortHills2017_stack.tif`（22 波段，30m，EPSG:2193）。
- **输出**：`A3/kmeans_diagnostic/kmeans_k{5,6,7}.png`(眼看) + `.tif`(叠 0.3m 航拍)。
- **结果（2026-09-18 跑）**：k=5 → **4 大簇(~1.0万px) + 1 小簇(715px)**；小簇在 k=6/7 稳定存在 → 真实独立类型（疑 bare-rock/水/建成）。簇空间连片 = 真结构，非噪声。
- ⚠️ **结论待定**：把 `kmeans_k5.tif` 叠 `A2porthills-fire/raster/PortHills_Aerial03m_2015.tif` 逐簇认名，才知 gorse/pine/native 分不分得开。分不开 → 合并 或 加特征(S2 red-edge / 季节 dNDVI)。
- ⚠️ 只作**诊断**（贴标签前），不是最终分类；定量可分性在 **US5**（JM + 光谱曲线）。

## 方法记录 · US1.4/1.5 LCDB reclass + 分层撒点（2026-09-18）

- **US1.4 对照表**：`lcdbPorthills` 加字段 `FuelClass`(文本)，Calculate Field 按 `Name_2012` 查表填值，Manuka/Kanuka 按易燃性归 `gorse_broom`（不按 native/exotic，见 product.md US1.4 完整对照表）。跑完分布：exotic_pine 50 个多边形、gorse_broom 37、pasture 17、native_scrub 16、Built-up 1(空值，排除，面积仅 0.05ha)。
- **US1.5 撒点**：`arcpy.management.CreateRandomPoints`，每类目标 50 点，最小间距 30m(避免同一 Landsat 像元里挤好几个点)。
  - ⚠️ **踩过的坑**：约束范围传入一个类的多个多边形时，这个工具是**每个多边形都撒够 N 个**，不是这一类总共 N 个——第一次跑出来 3604 点（该是 200）。**修法**：先 `Dissolve` 把同一类的多边形合并成一个整体，再撒点，N 才是这一类的总数。
  - 结果：4 类 × 50 = 200 点，存 `PortHills2017.gdb\TrainingPoints_raw`，字段 `FuelClass`/`class_id`(1-4，喂 GEE)/`split`。
- **训/验切分**：**没有**逐点随机 70/30——查资料发现这样切空间自相关会让验证精度虚高（[Spatial dependence between training and test sets 论文](https://link.springer.com/article/10.1007/s10994-021-05972-1)）。改成**按 300m 格子整块分配**（同一格子的点必须分到同一边），70/30 比例因此不精确（如 native_scrub 实际 58/42），这是有意的取舍。参考：[Choosing blocks for spatial cross-validation](https://www.researchgate.net/publication/390049401_Choosing_blocks_for_spatial_cross-validation_Lessons_from_a_marine_remote_sensing_case_study)、[Olofsson et al. 2014 分层抽样](https://research.wur.nl/en/publications/good-practices-for-estimating-area-and-assessing-accuracy-of-land/)。
- 脚本临时写在本机 `%TEMP%`，没进仓库（纯一次性数据操作，不是可复用管线）；逻辑摘要就是这段记录。

## 方法记录 · US1.6 bare-rock 补点（2026-09-19）

- LCDB 在 AOI 内没有对应类，只能靠地形+目视找。**第一版失败**：坡度>35° + 航片亮度高 当筛选条件——找出来的全是伐木道/冲沟（Port Hills 是玄武岩地貌，裸岩深灰色不亮，亮度筛选方向反了）。
- **第二版**：只用**坡度>60°**（近乎垂直，不管颜色），放大核对候选簇，3 个位置目视确认是真岩石（2 处海岸悬崖 + 1 处丛林圆丘状裸岩），其余是 DEM 拼接缝直线之类的假阳性，丢弃。
- 3 处各取 5 点（`scipy.ndimage.label` 连通域内随机采），共 15 点，插进 `TrainingPoints_raw`，`FuelClass='bare_rock'`/`class_id=5`，70/30 分（10/5）。
- ⚠️ 15 点明显少于其他类的 50 点——**报告里要写清楚这是局限**（这类本来稀少 + LCDB 无对应类，只能从少数目视确认点位取样，不是采样疏忽）。
- 三个确认点位坐标(NZTM)：`(1572834,5170644)` `(1569693,5168488)` `(1571720,5171724)`——回头 US1.6 剩下 4 类的抽验也可以顺手做。

## 方法记录 · 坡度/坡向核查 + exotic_pine 标签修正（2026-09-19）

- **坡向核查**：老师课上提过训练点要覆盖不同坡度/坡向（向阳背阳都要有）。查了 225 个点在 `Aspect1m.tif` 上的分布：`gorse_broom` 向阳明显多于背阳(11:4)——判断是真实生态规律（金雀花偏爱干燥向阳坡），不是取样偏差，写进报告当发现，不用改；`exotic_pine` 背阳只有 2 个、`bare_rock` 向阳/平地是 0——判断是取样没兜住，补点：exotic_pine 背阳坡补了 10 个；bare_rock 认真搜过向阳候选（坡度>60°里唯一像样的候选放大一看是伐木迹地边界，排除），**没找到向阳裸岩，判断是这片区域裸岩本来就集中在背阳/东向海岸悬崖**，写进报告当局限。
- **exotic_pine 标签修正**：亮度+绿度自动筛（活树冠深绿低亮度 vs 砍伐迹地浅棕高亮度）+ 目视核对，60 个 exotic_pine 点里筛出 4 个可疑，确认 3 个真的落在采伐迹地/集材场上（不是活树），删除；1 个是年轻松树苗（种植行清晰可见，不是砍伐迹地），保留。**原因**：LCDB `Class_2012` 标签是 2012 年的，松树有采伐周期，2012–2017 间被砍过的地块标签会过期失效——这是 **contextual outlier**（标签当年没错，时间点对不上导致现在失效），已写进 report.md R3 离群值那段。
- **最终点数（2026-09-19 收尾）**：222 点。`pasture` 35/15、`gorse_broom` 35/15、`exotic_pine` 38/19、`native_scrub` 29/21、`bare_rock` 10/5（train/valid）。

## 方法记录 · US1.4 新增第 6 类 cleared_pine（2026-09-19）

- **为什么加**：查 exotic_pine 训练点时发现有点落在采伐迹地上（LCDB `Class_2012` 标签是 2012 年的，松树有采伐周期，2012–2017 间被砍过的地块标签过期）。算了一下全 exotic_pine 范围（571.74ha）里"非郁闭林冠"面积：粗筛(亮度>110且绿度<5) 37.72ha(6.6%)，去掉 <100㎡ 噪点后 24.58ha——不是零star，够格单独成一类。
- **科学依据**：Scott & Burgan (2005) 标准火行为燃料模型体系，7 大组里专门有 **Slash-Blowdown (SB)** 一组，明确把采伐剩余物跟正常林分开算——燃料结构不一样（暴露、干燥、细小 vs 树冠层+阴凉林下），会实质影响燃烧行为，混在一起算会稀释 §4/§5 燃料类型 vs 燃烧结果这条关系。
- **踩过的坑——颜色识别这条路对这个类不管用**：试过用"跟一个确诊 slash 点颜色相似"去找同类区域(k-means 建调色板+欧氏距离阈值)：阈值松(20)匹配出 110.95ha(比粗筛还大，说明裸土/原木堆颜色太像干草坡，区分不出)；阈值紧(8)碎成 68 万个 <1㎡ 的噪点(说明真正该抓的是纹理——枝丫杂乱堆叠的质感，不是颜色，颜色这条路走不通)。**放弃颜色匹配，回退用粗筛+去噪点面积过滤的结果。**
- **类名从 "slash" 改成 "cleared_pine"**：目视核对撒出来的点，只有部分是教科书级别的原木堆/枝丫堆（100%确定的 slash），其余是林窗/稀疏地这种"非郁闭但不一定是新鲜伐木"的过渡状态——`cleared_pine`(exotic_pine 内非郁闭林冠区)比死抠"slash"更诚实、更站得住。
- **最终点数**：30 点（train 21 / valid 9），30m 最小间距过滤。**6 类总计 252 点**。

## 方法记录 · US2 核心点表建成（2026-09-19）

- 直接在本地用 `arcpy.sa.Sample()` 在 `PortHills2017_stack.tif`(22 波段) 上采样 252 个训练点，不走 GEE（点和栈都已经在本地同一个工程里，没必要绕云端）。
- ⚠️ **踩过的坑**：`Sample()` 输出表里有两个像 ID 的字段——`OBJECTID`(表自己新编的连续 1-N，没有意义)和以输入图层命名的字段（这里叫 `TrainingPoints_raw`，才是**真实的原始点 OID**）。第一版脚本用错了 `OBJECTID` 去拼标签，因为之前删过 3 个点留下缺口，导致从那之后**一半多的行波段值和标签全部对错位**——查"输出行数比点数少"这个异常线索才发现。**教训：Sample/ExtractValues 类工具的 ID 字段，认准以输入图层命名的那个，不是工具自己生成的 OBJECTID。**
- **QA 清洗**：查 `valid_data` 波段（标记云/云影像元），252 点里 41 个落在无效像元上（直接按坐标查栅格值查的，比只看 CSV 里 valid_data==0 更彻底，多抓到 2 个 NoData 的），删除。**最终 211 点**：pasture 45、gorse_broom 44、exotic_pine 43、native_scrub 46、bare_rock 10、cleared_pine 23。
- **产出**：`scripts/PortHills_PointTable.csv`（211 行 × 22 波段值 + FuelClass/class_id/split）——§3-§5 统计分析的地基，US2 完成。

## Lab 资源链接（Helen 给的 + lab 出处）

- **两份 lab PDF**：`A3/ERST619_L8_RelatingImageData2FieldData_FullDeck.pdf`（§3/§4 配方）、`A3/Week 1 - ERST310-Georef_2025_Learn.pdf`（配准 + 数字化训练数据）
- ArcPro 回归基础（Helen **强推**）：`pro.arcgis.com/en/pro-app/3.5/tool-reference/spatial-statistics/regression-analysis-basics.htm`
- ArcPro 标准化字段：`pro.arcgis.com/en/pro-app/3.5/tool-reference/data-management/standardizefield.htm`
- 数据变换/归一化：`datacamp.com/tutorial/how-to-normalize-data` · `geeksforgeeks.org/data-analysis/normalization-and-scaling`
- 回归类型（指数/对数图）：`monash.edu/student-academic-success/mathematics/exponential-and-logarithmic-functions`
- 离群值类型：`geeksforgeeks.org/data-analysis/types-of-outliers-in-data-mining`

---

## 环境记录 · J: 盘数据地图 + 本机自动化设置（2026-09-18 · 换电脑先看这段）

> 这段是**换机器/换 Claude 会话时的接续记录**，不属于报告内容。分两类：①**只在学校机器上有效**（J: 盘路径）②**结论本身可移植**（换哪台机器都成立的决定）。

### ① 只在学校机器有效：J: 盘数据地图

`J:\Data` 是学校共享 GIS 数据盘，只有在**学校机器**上挂载得到；换成自己电脑/别的机器这些路径全部失效，得改用 OneDrive 或重新下载。实测过（不是只看文件名）对这个项目有用的：

| 数据 | 路径 | 实测结论 |
|---|---|---|
| LCDB 分类 | `J:\Data\Landcover_Database_v5\...gdb`（也有 v6） | 511104 个多边形，NZTM，字段 `Class_1996/2001/2008/2012/2018`+`Name_*`；本项目训练标签种子用 `Class_2012` |
| 地形 DEM | `J:\Data\Digital_Elevation_Models\Christchurch_LiDAR_2021-2022\CHC_LiDAR_2020_21_DEM.tif` | **1m**，完整覆盖 Port Hills AOI，无空洞，高程 0–541m（对得上 Port Hills ~500m 顶）。同目录 `bpdem`/`bphs`（Banks Peninsula）只有 25m 且北界盖不全 AOI，别用 |
| 火前航片 | `J:\Data\Christchurch\Imagery\ChristchurchImage2015.gdb`（镶嵌数据集）+ `Tiles\` | 939 个 7.5cm(0.075m) 瓦片覆盖 AOI，"CAI URBAN IMAGERY 2015-16"，比项目里现成的 0.3m 航片更细，需要更高清底图判读时才换 |
| LiDAR 覆盖索引 | `J:\Data\ECan_LiDAR_Extents\`、`J:\Data\LiDARTiles\` | 查某片区有没有新 LiDAR，先看这两个索引 |
| 课程共享盘 | `J:\Courses\ERST619\` | 只有通用 lab 数据（Waimairi Beach LiDAR/大麦田/湿地监督分类/Thame 流域），**没有 Port Hills 专属数据**——真正的项目数据在自己的 OneDrive/本机项目文件夹，不在这 |
| 同类方法参考（非本项目数据） | `J:\Current_Projects\Fire\Knysna\Sven\` | 另一个人的南非 Knysna 2017 火 refugia 识别项目，结构类似（LULC+MODIS 火+refugia 点），卡壳时可以看方法思路，**不能当数据用** |

### ② 可移植的结论（换哪台机器都成立）

- **地形数据源**：原计划的粗分辨率/8m DEM → 换成 **1m LiDAR（Christchurch 2020-21 期）**。理由见 report R3：完整覆盖、分辨率够细、火后 LiDAR 当地形代理是合理的（地形不随火改变，30m 网格尺度可忽略局部侵蚀）。换机器没有 J: 盘时，找项目里已经裁好的 `PortHills_DEM8m.tif` 当备选，或找 OneDrive 里存的那份 1m 裁切结果。
- **训练标签**：LCDB **`Class_2012`** 字段（离 2017 火最近的火前期），不是 `Class_2018`。
- **判读底图必须火前**：2015 航片，不能用火后影像（workflow.md 阶段4 已强调，这里重复一遍因为踩过这坑）。
- **GIS 工程别塞进 git 仓库文件夹**：`.gitignore` 挡得住 git 追踪，但物理上把几个 GB 的 ArcGIS Pro 工程和轻量脚本仓库混一个目录很乱。约定：git 仓库（`a3/`）和 ArcGIS Pro 工程文件夹（`PortHills2017/`）**并排放**，不要嵌套。
- **OneDrive 同步 + ArcGIS Pro 工程 = 容易坏**：`.gdb`/大 `.tif` 放在实时同步的 OneDrive 文件夹里，ArcGIS Pro 编辑时容易被同步锁文件搞出问题。工程文件夹要放在**不同步或本地专属**的位置。
- **arcpy 是什么**（换电脑常问）：ArcGIS Pro 自带的 Python 包，等价于"用代码调 ArcToolbox 里的工具"，必须用 ArcGIS Pro 自己装的 python 解释器跑（`...\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe`），系统自带 python 里 `import arcpy` 用不了。
- **建 `arcpy.mp` 地图不会自动打开标签页**：`aprx.createMap(...)` 只是把地图加进工程结构，得去 Catalog/Project 面板 → Maps 里手动双击才能看到。

### ③ 本机自动化设置记录（MCP agent 桥，装过一次，换机器要重装但配方已验证）

调研过让 AI agent 直接操作 ArcGIS Pro 的办法（不止一种，见下），最后选了这个免费、本地、开源的：**`arcgis-pro-mcp-free`**(`github.com/IngKevinDavid/ArcGis-Pro-MCP-Free`，MIT，审过 C# 源码，只绑 `127.0.0.1`，无对外请求)。装法（换机器照抄）：

1. 下载/找到发布包（含 `package/ArcGisProMcpFree.esriAddinX` + `py-server/tcp_bridge.py` + 配套 wheel）。
2. 建个独立 venv（用 ArcGIS Pro 自带 python 建也行，因为需要 3.12+，ArcGIS Pro 3.6 自带的是 3.13.7），装那个 wheel。
3. 把 `.esriAddinX` 拷进 `Documents\ArcGIS\AddIns\ArcGISPro\`（不用双击装，拷贝就是装）。
4. **`claude mcp add arcgis-pro -s user -e PORT=5876 -- <venv>\Scripts\python.exe <path>\tcp_bridge.py`**——这条**必须用户自己在终端敲**，Claude 自己跑会被安全机制拦下来（"Create Unsafe Agents"），换电脑遇到一样的拦截很正常，不是 bug。
5. 重启 ArcGIS Pro → 功能区找 "MCP Free Bridge" 标签页 → 端口填一致（如 5876）→ 点 Start → 重启 Claude Code 会话让它认到新工具。

其他同类选项（没细装，仅供以后比较）：`arcpro-mcp`(qiobn)、`arcpy-mcp-server`(zhaojj662，1300+ 工具)、Esri 官方的 **ArcGIS Pro Tasks**(GUI 录制引导式流程，官方支持但没法用代码生成，得手动录)、**Python Toolbox (.pyt)**(完全代码生成的自定义工具，本项目已经建了一个 `PortHills_Tools.pyt`，随工程文件走，换机器一起带过去就行，不依赖任何额外安装)。

---

## 状态总览

- [ ] **⭐ 建核心点表**（栈在训/验点上采样 → 类别+波段+指数+地形一张表）= §3–§5 地基
- [ ] §2 目的（搬 A2 why 链，压 150 词）
- [ ] §3 清洗（复用 A1 脚本）
- [ ] §3 First pass 离群值（boxplot + IQR fences，表态 keep/delete；先删最重的再重算）
- [ ] §3 空值/常数列/重复行 清理
- [ ] §3 Second pass 正态性（hist+skew>\|1\|+kurt>\|2\|，点明 RF 不假设正态）
- [ ] §3 变换（测 log/sqrt/标准化，不做也 justify）
- [ ] §4 相关表 / cross-tab + 散点矩阵
- [ ] §4 回归（**定 #2**）+ MAE/RMSE/R² + 挂文献 + 精度评论
- [ ] §4 **多重共线性检查（VIF / 相关>0.8）**
- [ ] §5 训/验数据（配准+数字化 VegType）+ 可分性(JM+光谱曲线)
- [ ] §5 像元/对象 + RF + 为什么 + 引用
- [ ] §5 初步分类图 + 混淆矩阵 + 精度评论 + 挂文献
- [ ] §6 更新流程图（改 .dot，加统计层）
- [ ] §7 地图（6要素）
- [ ] §8 时间线（延到 A4+口试）
- [ ] 封面（标题/姓名/学号）

---

## 建议的下一步（一次一件）

读完两份 lab，现在最该先落地的是**那张"训练/验证点表"** —— 它是 §3、§4、§5 全部的地基，没有它后面统计无从做起。它需要：①训/验点（配准+数字化，或先用 LCDB 现成点起步）②把 6 波段+指数+地形栈在这些点上采样成属性表。

所以下一件事（一次一件），二选一：
1. **搭点表**：先用你 A1 已有的栈 + LCDB 点，采样出第一版属性表（最省力、最地基）。
2. **定 #2 回归**：把 dNBR-线性 vs 类别-逻辑 这个决定先敲定（这样 §4 才能动）。

你说从哪块开始，我给料、你写句子/做决定。
