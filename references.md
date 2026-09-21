# A3 References — 事实底座（给两台机的 Claude 当引用依据，别瞎编）

> ⚠️ 给 AI 读的：**只引这里列出的**；标 ✅=已核实出处，⏳=未核实（用前 Yu 自己点开确认年份/作者）。
> ⚠️ 老师要的"3 篇 published articles"只能用 **A 组**；B 组只当"事实数据"引；不确定的**别写进报告**。
> ⚠️ 这是 Yu 自己写的文献笔记（非 PDF 再分发）。期刊 PDF 在本地 `refine/A2_参考文献/`，因版权**不进库**。

---

## A. 同行评审文章（老师要的"3 篇"从这选）

**A1. Meddens et al. (2018)** — refugia 是什么/为什么重要（概念地基）✅
- *Fire Refugia: What Are They, and Why Do They Matter for Global Change?* BioScience 68(12), 944–954. DOI 10.1093/biosci/biy103
- 用于：§2 目的、§5/limitations（ephemeral refugia 定义——你只一场火 → 用 ephemeral，别用 persistent）

**A2. Krawchuk et al. (2016)** — 地形控制 refugia（correlates 机理）✅
- *Topographic and fire weather controls of fire refugia…* Ecosphere 7(12), e01632. DOI 10.1002/ecs2.1632
- 用于：§4 correlates 选择依据（aspect/slope/TWI）

**A3. Wyse et al. (2016)** — ⭐核心角度：NZ 植被易燃性 ✅
- *A quantitative assessment of shoot flammability for 60 tree and shrub species…* Int. J. Wildland Fire 25(4), 466–477. DOI 10.1071/WF15047
- 要点：**gorse (Ulex europaeus) 最易燃**；提出低易燃物种做 green firebreaks。
- 用于：§2 目的、§5 **分类体系**（按易燃性归类 → 所以 mānuka/kānuka 进 gorse_broom、阔叶原生进 broadleaf_scrub）

**A4. Christ et al. (2025)** — ⭐Kaupapa 方法母本（de Klerk 署名）✅出处
- *Predicting Persistent Forest Fire Refugia Using Machine Learning…* ISPRS Int. J. Geo-Inf. 14(12), 480. DOI 10.3390/ijgi14120480
- 要点：变量=aspect/slope/elevation/TWI/TCI/TRI/solar/wind；**RF + ensemble**；aspect 头号因子。⚠️研究区南非。
- 用于：§4 correlates、§5 **RF 方法依据**

**A5. Krawchuk et al. (2025)** — refugia 概念+应用综述 ✅全文已读
- Conservation Science and Practice, e70173. DOI 10.1111/csp2.70173
- 要点：stochastic↔persistent；30m Landsat 尺度；诚实调子。用于：概念 + §6 limitations 语气。

**A6. Coppoletta, Merriam & Collins (2016)** — 火后植被驱动重烧烈度（2024火场复现新找的）✅出处核实过（treesearch.fs.usda.gov 摘要页读的全文）
- *Post‐fire vegetation and fuel development influences fire severity patterns in reburns.* Ecological Applications 26(3), 686–699. DOI 10.1890/15-0225
- 要点：加州内华达山脉4场火(2000-2010)、2012年被重烧的跟踪研究——高烈度初次火→枯立木+灌丛增多→跟恶劣火天气叠加→重烧时更容易高烈度。
- 用于：解释2024火场为什么cleared_pine占比这么大(金雀花从19.5%涨到30.0%)——不是巧合，是文献记录过的机制，跟Wyse2016(金雀花易燃本身)是互补角度。

---

## B. 报告/数据源（只引"事实数据"，不算"3 篇"）
- **B1 WMO (2025)** ✅ 2024=1.55°C，首个全年破 1.5°C。
- **B2 NIWA (2020)** Canterbury 气候投影 ⏳
- **B3 Scion/MPI (Pearce/Watt)** NZ 火险上升、点名 Canterbury ⏳
- **B5 Banks Peninsula 清林史**（1900 前砍 99%、gorse 入侵）⚠️引前须找学术源

---

## C. 指数/方法标准引用
- NDVI → Rouse et al. (1974) · NBR/dNBR → Key & Benson (2006) · NDWI → McFeeters (1996) · NDRE → Barnes et al. (2000)
- **RBR（相对化燃烧比 · 异质植被 SOTA 严重度度量）** → **Parks, S.A.; Dillon, G.K.; Miller, C. (2014)** *A New Metric for Quantifying Burn Severity: The Relativized Burn Ratio.* Remote Sensing 6(3), 1827–1844. DOI 10.3390/rs6031827。公式 `RBR = dNBR / (NBR_pre + 1.001)`；实测优于 dNBR/RdNBR（R² 0.786>0.761>0.766），修正 dNBR 被火前生物量绑架的偏差——A3 §4 用作连续 Y（主线回归）。RdNBR 前身 → Miller & Thode (2007)。

---

## D. A3 期间新增方法引用（确切 citation 见 `report.md` 已挂链接，用前核）
- **Hansen et al. (2013)** *High-Resolution Global Maps of 21st-Century Forest Cover Change.* Science 342, 850–853. → 用于 cleared_pine 用森林损失定义 + 火前伐木检测 ✅（知名，出处稳）
- **Olofsson et al. (2014)** *Good practices for estimating area and assessing accuracy of land change.* Remote Sensing of Environment 148, 42–57. → 精度评估/样本量 ✅
- **空间分块训练/验证**（避免空间自相关）→ report.md R5 已挂 Ploton / Karasiak 等链接，⏳ 用前核确切作者年份。
- **JM 可分性 / 图像分类** → Richards, J.A. (2013) *Remote Sensing Digital Image Analysis* (Springer)。⏳ 核版次/页。
- **gorse 卫星制图（花期黄）** → 08 脚本引 "Satellite mapping of gorse at regional scales"（researchgate 230694091）⏳ 补确切作者年份再用。
- **Cohen's d（效应量）** → Cohen, J. (1988) *Statistical Power Analysis for the Behavioral Sciences.* → 用于报告红边/花期分离度描述。
- **SHAP（可解释性 · 取代/补 Gini 变量重要性 · 给方向+局部+交互）** → **Lundberg, S.M.; Lee, S.-I. (2017)** *A Unified Approach to Interpreting Model Predictions.* NeurIPS 30。→ §5 变量重要性 + §4 "哪个 correlate 决定 refugia/严重度"；2024-25 火险/严重度制图的标准 XAI 工具。
- **树集成 > 深度学习（表格数据 · justify 用 RF 不用 CNN）** → **Grinsztajn, L.; Oyallon, E.; Varoquaux, G. (2022)** *Why do tree-based models still outperform deep learning on tabular data?* NeurIPS 35 (Datasets & Benchmarks)。→ §5 为什么少样本表格数据用 RF/提升树而非深度学习。
- **（可选）XGBoost（梯度提升 · RF 的对比模型）** → **Chen, T.; Guestrin, C. (2016)** *XGBoost: A Scalable Tree Boosting System.* KDD。→ §5 若加 RF vs 提升树并排对比。
- **Google Satellite Embedding / AlphaEarth Foundations（预训练 EO 基础模型嵌入 · 当额外特征喂 RF · A4 方向）** → **Google DeepMind (2025)** *AlphaEarth Foundations: An embedding field model for accurate and efficient global mapping from sparse label data.* arXiv 2507.22291；GEE 数据集 `GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL`（64 维 / 10m / 年，"像波段一样"可在点上采样）。→ **A4 way-forward**：稀疏标签下嵌入喂 RF 标签效率极高（5% 样本近饱和），编码整年物候 → 攻 gorse↔broadleaf(JM=1.46)。⚠️年度嵌入约 2017 起 → 2024 火(火前 2023)比 2017 火(2016 没覆盖)更适用。

---

## E. 2024火场复现 — 待核（WebFetch被403/跳转拦了，Yu 自己浏览器打开确认）
> 这几条我只读到 WebSearch 摘要，**没读到全文**，标题/年份/方法描述都可能有偏差——
> 点开链接自己核实之后再引用，核实之前当"线索"不当"事实"。

- **⏳E1** 疑似 2025年，*Fire* 期刊 (MDPI) 8(6):230，DOI `10.3390/fire8060230`（打开会跳转到
  `mdpi.com/2571-6255/8/6/230`）。主题：用 BULC-D 算法测华盛顿州2020火的"durable fire
  refugia"+ delayed canopy loss，多传感器时间序列。如果以后想把 refugia 那步(US7等效)
  做得比现在的 dNBR 阈值更严谨，这个方向的候选方法。
- **✅E2 已核实全文**（本地 PDF `s42408-023-00218-y.pdf` 全文读过，2026-09-21）：**Solares-Canal, A.;
  Alonso, L.; Rincón, T.; Picos, J.; Molina-Terrén, D.M.; Becerra, C.; Armesto, J. (2023).**
  *Operational fuel model map for Atlantic landscapes using ALS and Sentinel-2 images.*
  **Fire Ecology 19:61.** DOI 10.1186/s42408-023-00218-y
  - 研究区：西班牙 Galicia（大西洋气候，植被生长快、燃料积累快，跟地中海不同）。S2 逐月时序 + 机载 LiDAR，
    Rothermel 燃料模型，**Random Forest** 分类；土地覆盖图 **OA 90% / Kappa 0.88**，UA/PA 70–100%。
  - 方法要点（可借的）：① **"每个统计量单独出成一张栅格，便于逐一分析、对照参考影像解读、与其他统计量比较"**
    ——逐变量探索的文献背书；② 变量重要性 = **mean decrease in Gini**（引 Breiman & Cutler）；③ LiDAR 统计量里
    直接含 **skewness / kurtosis / entropy / CV / 各分位**（Table 3）——背书用偏度峰度描述分布；④ **逐月 12 景时序**
    抓物候 + plurality voting 聚合；⑤ 波段重采样到统一分辨率（nearest neighbor）、用 L2A 云掩膜清洗。
  - 用于：📖 撑 CHM+S2 燃料分类方法先例；📖 §3 逐变量探索 + §5 RF/Gini 重要性 的可引出处；
    多时相物候 → §6 way forward（分 gorse/broadleaf）。
- **✅E3 已核实全文**（本地 PDF `remotesensing-12-03660.pdf` 全文读过，2026-09-21；此前只读到 frames.gov 摘要）：
  **Domingo, D.; de la Riva, J.;
  Lamelas, M.T.; García-Martín, A.; Ibarra, P.; Echeverría, M.T.; Hoffrén, R. (2020).**
  *Fuel type classification using airborne laser scanning and Sentinel-2 data in Mediterranean
  forest affected by wildfires.* **Remote Sensing 12(21):3660.** DOI 10.3390/rs12213660
  - 方法：ALS + Sentinel-2 + 136 野外样方；SVM(径向核)；关键特征=25th 分位高度、均值以上回波占比、
    rumple 结构多样性、NDVI；**OA 59%**。
  - ⭐ **变量筛选方法（全文才读到，§3/§4 可借）**：① 用 **Spearman 秩相关(ρ)** 定各特征跟燃料类型关系的
    强度+方向，卡阈值(相关>0.65)选特征——**不是 Pearson**；② 另试 **all-subset selection**（穷举/后向/前向/
    序贯替换）自动选子集，结论：没比 Spearman 选法更好；③ 变量重要性用 **drop-one**（逐个删特征看 OA 掉多少，
    删"均值以上回波占比"掉 0.14）；④ 验证=分层随机抽 25% × 跑 100 次取均值。
  - ⚠️ **RF 过拟合警示**：他们 RF 拟合 0.99、验证只有 0.56（巨大落差）——可当本研究 RF(OOB 0.627→验证 0.71，
    落差小得多)的反例对照，撑 §5 精度评论。
  - 用于：📖 撑 **CHM(ALS高度)+S2 燃料分类**方法先例 + **精度基准**（本研究 RF ~68% > 其 59%）；
    📖 §4 Spearman 秩相关选特征的可引出处；可借"rumple 结构多样性 / 高度分位"特征。

---

## F. 候选方法 → 文献映射（2026-09-21 读 E2/E3 全文挖的）

> ⚠️ **决定/验证状态不在这**：采不采、跑没跑、适不适合 2017 → 看 `product.md` 的「🟡 2017 改进候补」表（一处真相）。
> 这里只留**方法 ↔ 出处 ↔ 喂哪节**的对照，方便写报告时查引用。都是 📖 外部文献可引。

| # | 候选办法 | 出处 | 对哪节 | 新活 or 补引用 |
|---|---|---|---|---|
| F1 | **Spearman 秩相关**并排跑一版（对比 Pearson+VIF）：不要求正态、抓单调关系，把 §3"多变量非正态"发现和 §4 相关分析串成因果链 | E3 Domingo2020 | §4（连 §3） | ⭐新活（已跑，见 `scripts/04e_spearman_correlation.py`） |
| F2 | "每个变量单独出图、对照参考影像逐一解读"当 §3 探索方法背书 | E2 Solares2023 | §3 | 补引用 |
| F3 | 变量重要性 = mean decrease in Gini 出处；另可加 **drop-one** 法 | E2 Solares / E3 Domingo | §5 | 补引用 + drop-one 可选新活 |
| F4 | RF 过拟合反例(Domingo 拟合0.99/验证0.56) 对照本研究健康落差 | E3 Domingo2020 | §5 精度评论 | 补弹药 |
| F5 | skew/kurt 当标准分布描述量的背书 | E2 Solares2023 Table3 | §3 正态性 | 补引用 |
| F6 | 多时相/物候分 gorse↔broadleaf(JM=1.46 最弱对) → **具体工具 = Google Satellite Embedding**(AlphaEarth, GEE 现成 64 维/年嵌入, 采点喂 RF) | E2/E3 + AlphaEarth(D 组) | §6 / **A4 way-forward** | ✅**已定加进 A4**(2026-09-21)；免训练、稀疏标签设计、不离 GEE+RF |

> ⚠️ E2/E3 都是同行评审文章、方法直接对口(ALS+S2 燃料分类)——可考虑当 Helen 要的"3 篇"或方法先例引；是否从 E 组升进 A 组，Yu 定。

---

## 一眼查：哪篇喂 A3 哪节
| A3 节 | 主要引用 |
|---|---|
| §2 目的 | WMO(B1) + Scion/NIWA(B2/B3) + Wyse(A3) + Meddens(A1) |
| §3 数据探索 | 指数(C 组)【候选 +E2 F2/F5】 |
| §4 关系/correlates | Christ(A4) + Krawchuk2016(A2) + Olofsson【候选 +E3 F1 Spearman】 |
| §5 分类体系 | Wyse(A3)（按易燃性） |
| §5 训练数据 | Hansen(cleared_pine) + Olofsson + 空间分块(D) |
| §5 分类方法(RF) + 可分性(JM) | Christ(A4) + Richards(D)【候选 +E2/E3 F3/F4】 |
| §6 limitations | Krawchuk2025(A5) 的诚实调子【候选 +F6 多时相】 |
