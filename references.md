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

---

## B. 报告/数据源（只引"事实数据"，不算"3 篇"）
- **B1 WMO (2025)** ✅ 2024=1.55°C，首个全年破 1.5°C。
- **B2 NIWA (2020)** Canterbury 气候投影 ⏳
- **B3 Scion/MPI (Pearce/Watt)** NZ 火险上升、点名 Canterbury ⏳
- **B5 Banks Peninsula 清林史**（1900 前砍 99%、gorse 入侵）⚠️引前须找学术源

---

## C. 指数/方法标准引用
- NDVI → Rouse et al. (1974) · NBR/dNBR → Key & Benson (2006) · NDWI → McFeeters (1996) · NDRE → Barnes et al. (2000)

---

## D. A3 期间新增方法引用（确切 citation 见 `report.md` 已挂链接，用前核）
- **Hansen et al. (2013)** *High-Resolution Global Maps of 21st-Century Forest Cover Change.* Science 342, 850–853. → 用于 cleared_pine 用森林损失定义 + 火前伐木检测 ✅（知名，出处稳）
- **Olofsson et al. (2014)** *Good practices for estimating area and assessing accuracy of land change.* Remote Sensing of Environment 148, 42–57. → 精度评估/样本量 ✅
- **空间分块训练/验证**（避免空间自相关）→ report.md R5 已挂 Ploton / Karasiak 等链接，⏳ 用前核确切作者年份。
- **JM 可分性 / 图像分类** → Richards, J.A. (2013) *Remote Sensing Digital Image Analysis* (Springer)。⏳ 核版次/页。
- **gorse 卫星制图（花期黄）** → 08 脚本引 "Satellite mapping of gorse at regional scales"（researchgate 230694091）⏳ 补确切作者年份再用。
- **Cohen's d（效应量）** → Cohen, J. (1988) *Statistical Power Analysis for the Behavioral Sciences.* → 用于报告红边/花期分离度描述。

---

## 一眼查：哪篇喂 A3 哪节
| A3 节 | 主要引用 |
|---|---|
| §2 目的 | WMO(B1) + Scion/NIWA(B2/B3) + Wyse(A3) + Meddens(A1) |
| §3 数据探索 | 指数(C 组) |
| §4 关系/correlates | Christ(A4) + Krawchuk2016(A2) + Olofsson |
| §5 分类体系 | Wyse(A3)（按易燃性） |
| §5 训练数据 | Hansen(cleared_pine) + Olofsson + 空间分块(D) |
| §5 分类方法(RF) + 可分性(JM) | Christ(A4) + Richards(D) |
| §6 limitations | Krawchuk2025(A5) 的诚实调子 |
