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
| 分类体系（A2 定的 5 类） | pasture / gorse-broom(高易燃) / exotic pine / native scrub(低易燃) / bare-rock | 🔲 |

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
| 3 | 训/验怎么分 | 70/30 · 面积比例 · 空间块 · 少类过采样 | 🔲 |
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

## Lab 资源链接（Helen 给的 + lab 出处）

- **两份 lab PDF**：`A3/ERST619_L8_RelatingImageData2FieldData_FullDeck.pdf`（§3/§4 配方）、`A3/Week 1 - ERST310-Georef_2025_Learn.pdf`（配准 + 数字化训练数据）
- ArcPro 回归基础（Helen **强推**）：`pro.arcgis.com/en/pro-app/3.5/tool-reference/spatial-statistics/regression-analysis-basics.htm`
- ArcPro 标准化字段：`pro.arcgis.com/en/pro-app/3.5/tool-reference/data-management/standardizefield.htm`
- 数据变换/归一化：`datacamp.com/tutorial/how-to-normalize-data` · `geeksforgeeks.org/data-analysis/normalization-and-scaling`
- 回归类型（指数/对数图）：`monash.edu/student-academic-success/mathematics/exponential-and-logarithmic-functions`
- 离群值类型：`geeksforgeeks.org/data-analysis/types-of-outliers-in-data-mining`

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
