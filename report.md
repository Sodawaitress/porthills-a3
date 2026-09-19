# A3 报告写作 — 一段一段写（跟着分析 US 走）
> 报告不是最后憋出来的：**每做完一个分析 US，立刻写它喂的那段**。写在你自己的 Word/Google Doc 里。
> 这份是**提纲 + 中文写作提示**，帮你组织思路。
> 截止 **2026-09-23** · ~2000 词 / 5–10 页 · 顺序照 rubric · 满分 100。

---

## 🔵 现在能写：R1 封面 + R2 目的（料在 A2，不用等分析）

**R1 封面**：标题 · 全名 · 学号。

**R2 目的**（下面 R2 提示照着写）。

---

## 报告 backlog（R1–R8 · 对齐 rubric · 喂它的分析 US · 写在做完之后）

| R | 报告节 | 分 | 喂它的分析 US | 何时能写 | 状态 |
|---|---|---|---|---|---|
| R1 | 封面 | 0 | — | 随时 | 🔵 |
| R2 | 目的（Wegmann Step1） | 5 | 料在 A2 | 随时 | 🔵 |
| R3 | 数据探索 | 20 | US2 + US3 | US3 做完 | 🔲 |
| R4 | 关系（相关/回归/VIF） | 25 | US4 | US4 做完 | 🔲 |
| R5 | 分类 | 27 | US1 + US5 + US6 | US6 做完 | 🔲 |
| R6 | 流程图 + way forward | 10 | US8 | US8 做完 | 🔲 |
| R7 | 地图 | 4 | US6 / US7 / US9 | 图出来后 | 🔲 |
| R8 | 时间线 | 4 | US10 | 最后 | 🔲 |

> 规则：分析 US 的 loop 第 6 步 = 写它喂的这段 R。**别攒到最后。**

---

## 各节写作提示（中文提示帮你组织）

### R2 目的（5分 · Wegmann Step1 · ~120词）
- 一句：**科学上**为什么要一张植被/燃料分类图？（挂气候暖化→Canterbury 火险→gorse 清林遗产；见 A2 why 链）
- 一句：你会拿它**做什么**？（叠 refugia×植被×地形 → 低易燃种植 / firescaping）
- 一句：为什么非要"分类图"？（卫星只给反射率数字，只有分类才能给每处贴植被标签，烧/不烧才对得上号）

### R3 数据探索（20分 · 喂：US2 点表 + US3）
- **空间清洗**（5）：你做了什么 + 为什么（缩放到反射率 / 云影掩膜 / 裁 AOI / NZTM）。
  - ⭐ 已定：地形层用 **Christchurch LiDAR 2020-21（1m）**，不用原计划的粗分辨率 DEM。理由：完整覆盖 AOI 无空洞，分辨率细过唯一的本地替代（Banks Peninsula 25m，且北界盖不全 AOI）。局限：LiDAR 是火后期采集，但地形本身不因火改变（30m 网格尺度下局部侵蚀可忽略）——这条局限也要写。
- **离群值**（5）：boxplot 看到哪类离群？**keep 还是 delete，为什么**（真信号 vs 云/传感器伪影）。
  - ⭐ 已发现一例真实案例（训练点层面，不是波段层面，但是同一个道理）：`exotic_pine` 训练点里有 3 个落在**采伐迹地/集材场**（不是活树），亮度+绿度筛+目视核对确认后删除。原因：LCDB `Class_2012` 标签是 2012 年的，松树有采伐周期，2012-2017 间被砍的地块标签就过期了——**这是 contextual outlier（标签本身没错，但时间点对不上导致失效）**，不是传感器伪影。保留了 1 个视觉上是"年轻松树苗"的点（不是砍伐迹地，只是树龄小），因为它仍是真实的 exotic_pine。
  - ⭐ **像元纯度检查**：以每个训练点为中心画 15m 半径（对应 30m Landsat 像元宽度），检查是否越出其所在 LCDB 多边形——178 个点里 28 个(15.7%)"不纯"（15m 范围内碰到别的类别），说明这些点对应的 Landsat 像元本身就是混合像元，直接删除并在各类别向内缩 15m 后的安全区域内重新撒点补齐。这是空间意义上的离群值处理，同样服务"keep or delete + why"这条。
  - ⭐ **重复行**：`bare_rock` 10 个点里查出 5 行数值完全重复，原因是岩石点位只有35-40m见方，30m最小间距不足以保证每个点落进不同的30m Landsat像元——去重后 bare_rock 只剩 **7 个真正独立的点**，这是这一类的真实局限（稀少+空间挤），报告要点明。
- **正态性**（5）：哪些波段 **skew>|1| / kurt>|2|** = 非正态？列出来下结论。
  - ⭐ **关键方法论发现**：12 个变量混合全部 6 类一起算偏度/峰度，**全部"通过"正态检验**；但直方图显示好几个变量明显多峰（尤其 `northness` 两端各一峰）——偏度/峰度对"多峰"不敏感，混合类别天然产生多峰，数字上测不出来。**改成按类别分别检验**，72组(6类×12变量)里 **19组超标**，其中 `native_scrub` 的 `NBR_pre`(偏度-2.95)、`NDVI`(偏度-2.18)最严重。按数值排序定位到具体的点，发现正是之前目视抽查标记过的边界可疑点——两条独立路径（目视+统计）指向同一个点，删除后偏度/峰度大幅改善（NBR_pre降到-1.79，NDVI降到-1.48），非正态组合数19→17。**结论：正态性检验应该按类别分开做，不能在混合类别的点表上直接跑。**
- **变换**（5）：试了哪个（log/sqrt/标准化）、为什么、改善没；**若不做 → 为什么不做**（挂"RF 尺度不变"）。
  - ⭐ 已测：对最严重的几组分别试 log/sqrt——**右偏**的变量（`exotic_pine`/`gorse_broom` 的原始波段，偏度1.4-1.5）log 后明显改善，`gorse_broom pre_B7` 甚至从1.51降到0.13、完全达标；但**左偏**的变量（`native_scrub` 的 `NDVI`/`NBR_pre`，偏度-1.5~-1.8）log/sqrt 反而让偏度更极端(-1.79→-2.59)——因为 log/sqrt 专门压缩右边长尾，用反方向只会加重左偏，不是通用解法，得先判断偏的方向再选变换。z-score 标准化不改变分布形状(只改尺度)，偏度峰度理论上跟原始一样，验证过确实如此。
  - **最终决定：分类步骤不做变换**——RF 对单调变换/尺度不敏感，做了也不影响分类结果；但探索证明了懂每种变换的适用边界（而非套公式），满足"调查过+说明为什么不做"这条。

### R4 关系（25分 · 喂：US4）
- **相关表**（5）：⭐ 已算：跟 dNBR 相关最强的是 `NDVI`(0.475) 和 `BSI`(-0.460)——火前越绿烧得越重(燃料够烧)，裸土越多烧得越轻(没什么好烧)，符合直觉；`elev` 几乎零相关(-0.014)，高程本身不直接预测烧毁程度。
- **散点**（5）：⭐ 已出图(`exploration/scatter_dnbr.png`)：6个清理后的变量 vs dNBR 全部呈**线性**关系(没有曲线形状)，支持用线性回归。单变量里 `NDVI`(R²=0.226)最强，`pre_B5`(0.163)、`northness`(0.129，向阳坡烧得更重，符合干燥易燃逻辑)其次；`elev`(R²≈0，p=0.84)、`slope`(R²=0.018，p=0.05压线)基本不相关。单变量都不强，合起来能到R²=0.41，是多个弱信号叠加的效果。
- **哪种回归 + 为什么**（5）：**决定#2 定了：选①**，dNBR 当连续 Y 跑线性回归（预测变量=火前波段/指数/地形）。理由：对齐 lab 教的 GLR 连续例子；直接服务 refugia 问题("火前状态能不能预测烧多重")；能出 R²/RMSE。查文献支持这个选择——2024-2026 年最新烧毁强度预测研究普遍用连续预测变量+回归/RF回归框架(Utah研究R²=67%，LA研究解释~60%方差)，跟本项目思路一致。
- **多重共线性/VIF**（融进这25分里）：⭐ 已做：波段+指数原始 VIF 高达 47-99（`BSI`/`pre_B6`/`NDVI` 最严重），远超 lab 给的 7.5 门槛，按 lab 教的规矩**迭代删除 VIF 最高的变量**，5轮后收敛到 6 个变量（`pre_B5`/`pre_B7`/`NDVI`/`elev`/`slope`/`northness`），全部 VIF≤7.5。
- **结果 + 解读 + 挂文献**（5）：清理后模型 R²=0.413，调整R²=0.395，RMSE=231.55，MAE=189.77——中等解释力，符合"火前光谱+地形只能解释四成左右烧毁程度变化"的预期(还有天气、火行为等模型没包含的因素)。
  - ⭐ **额外发现（比复述文献更有分量）**：把 `FuelClass`(哑变量) 加进清理后的模型，R² 提升到 0.476，F检验 p=0.0004(高度显著)——**这跟 2024 年 Utah 那篇论文的结论相反**（他们发现土地覆盖类别加了不提升模型），可能原因：本项目的 6 类是专门为火险设计的细分类别(含 cleared_pine/bare_rock 这种通用土地覆盖不会有的类)，携带了光谱波段本身没完全捕捉到的信息——这是个可以在讨论里挂文献、正反对比着讲的点。
- **精度评论**（5）：R²=0.41-0.48 中等，RMSE=220-230(dNBR原始量级几百到上千，误差不算小)；可能的改进方向——加入火行为/天气变量、扩大训练点、或换用 RF 回归(见R6 way forward)。

### R5 分类（27分 · 喂：US1 训练点 + US5 可分性 + US6）
- **训练/验证数据**（5+5）：收了什么点、怎么收（**2015 0.3m 航拍判读** + LCDB `Class_2012` 当种子）、多少（**6 类共 252 点**）、怎么分（70/30，空间分块）。
  - ⭐ 已定：**A2 原定 5 类扩到 6 类**，新增 `cleared_pine`（exotic_pine 内非郁闭林冠区）。理由：exotic_pine 全域 571.74ha 里有一部分是新鲜伐木迹地/林窗，LCDB 标签是 2012 年的，跟不上松树采伐周期；按 [Scott & Burgan (2005) 标准火行为燃料模型](https://en.wikipedia.org/wiki/Fuel_model) 惯例，采伐剩余物(Slash-Blowdown)本就该跟正常林分开算，燃料结构（暴露干燥细小 vs 树冠+阴凉林下）不同，混在一起会稀释燃料类型与烧毁结果的关系。
  - 方法迭代：最初用亮度+绿度粗筛（目视核对发现精度一般），后改用 **Hansen Global Forest Change**（`UMD/hansen/global_forest_change_2023_v1_11`，`lossyear==16`，权威可引用的全球森林变化监测数据集）定位 2016 年发生的森林损失，只保留连通像元≥6(~0.5ha)的成块区域。发现候选点空间分布不均（扎堆在少数几个采伐区，最近两点仅22m，比一个Landsat像元还窄），加两条约束修正：30m最小间距 + 每个采伐区最多3个点，最终28个点分布到16个不同区块，最近距离43m、中位数间距106m。
  - ⭐ 已定：70/30 **不是逐点随机分的**，是按 300m 空间格子整块分配（同一格子的点必须分到同一边）。理由：逐点随机切分会有空间自相关，训练/验证点离得太近导致验证精度虚高，这是遥感分类评估的一个常见坑。引用：
    - Ploton et al. 相关综述：[Spatial dependence between training and test sets: another pitfall of classification accuracy assessment in remote sensing](https://link.springer.com/article/10.1007/s10994-021-05972-1)
    - 分块方法参考：[Choosing blocks for spatial cross-validation: lessons from a marine remote sensing case study](https://www.researchgate.net/publication/390049401_Choosing_blocks_for_spatial_cross-validation_Lessons_from_a_marine_remote_sensing_case_study)
    - 分层抽样一般原则：[Olofsson et al. 2014, Good practices for estimating area and assessing accuracy of land change](https://research.wur.nl/en/publications/good-practices-for-estimating-area-and-assessing-accuracy-of-land/)
  - 局限：300m 格子大小是经验取值（约 10 个 Landsat 像元），不是从半变异函数算出来的最优值，70/30 比例因此没卡死（比如 native_scrub 实际是 58/42）——这个取舍也值得在报告里说一句。
  - ⭐ 已定：**bare-rock 不是第 5 种"植被类型"，是非燃料(non-burnable)对照类**——按 Scott & Burgan (2005) 标准火行为燃料模型体系的惯例单列（该体系明确把 Urban/Snow-Ice/Agricultural/Water/Bare-Ground 列为非燃料类，不与可燃燃料类并列）。用于在 refugia 分析里排除"因无燃料而未燃烧"的像元，避免和"因植被/地形而幸存"的真实 refugia 信号混淆。引用：
    - [Fuel model (Scott & Burgan 非燃料类 NB1/NB8/NB9)](https://en.wikipedia.org/wiki/Fuel_model)
    - [Standard Fire Behavior Fuel Models: A Comprehensive Set (NIFC/GACC)](https://gacc.nifc.gov/oncc/docs/40-Standard%20Fire%20Behavior%20Fuel%20Models.pdf)
    - [Forest and Rural Fire Danger Rating in New Zealand — Stuart Anderson](https://fgr.nz/wp-content/uploads/2024/06/10-NZFDRS.pdf)
- **可分性**（5）：⭐ 已做（`exploration/spectral_profile_6class.png` + JM矩阵，脚本`scripts/05_separability_jm.py`）。JM指数(0~2，越大越好分)用6波段+NDVI+BSI算：**`bare_rock` 跟其余5类全部完全分开(JM=2.00)**；其余类间大多也分得不错(JM 1.9-2.0)；但 **`gorse_broom` vs `native_scrub`(JM=1.46)明显是最弱的一对**——光谱曲线图上这两条线在B5/B6/B7几乎重合。这**直接呼应了项目最早期(US1.1 k-means诊断)就担心的那个问题**("native vs gorse分不分得开")，现在用JM给出了定量证据：这两类确实存在真实的光谱混淆风险，§5分类结果如果这两类互相误判多，这里就是原因，不是模型的锅。引用 Richards (2013) *Remote Sensing Digital Image Analysis* 的JM公式。
- **像元/对象 + 为什么**（2）：像元法(pixel-based)，不是对象法(object-based)。理由：A2就倾向像元RF；训练点本来就是逐像元采样的，跟点表结构一致；对象法要先分割，本项目训练数据量不大(211点)，分割反而可能引入额外噪声。
- **算法 RF + 为什么 + 引用**（5）：Random Forest。理由：样本量小(每类10-46个)时比深度学习更稳定、不容易过拟合；能输出变量重要性，方便解释"哪个波段/地形对分类贡献大"；不需要假设正态分布，跟本项目§3发现的"混合类别非正态"问题无缝衔接。用 `sklearn.ensemble.RandomForestClassifier`(500棵树)，训练/验证用之前定好的空间分块split，不是重新随机分。
- **结果 + 混淆矩阵解读 + 挂文献**（5）：⭐ 已跑（`exploration/rf_confusion_matrix.png`，脚本`scripts/06_random_forest_classify.py`）。**OA=0.710，Kappa=0.638**(按Landis&Koch(1977)分级，0.61-0.80="substantial agreement"，中等偏上)。混淆矩阵最大的误判：**`native_scrub`→`gorse_broom` 错了7个**(20个真实native_scrub里)，`gorse_broom`→`exotic_pine`/`native_scrub`各错2个——**跟US5的JM指数(gorse_broom vs native_scrub=1.46，全部15对最低)完全对上**，不是模型没调好，是这两类本身光谱就像。`cleared_pine`(PA=UA=1.00)和`pasture`/`exotic_pine`(PA=0.8)分类效果好。特征重要性：`BSI`/`pre_B5`/`pre_B4`/`pre_B3`最重要，地形变量(`elev`/`northness`)排最后——光谱信息比地形对分类贡献更大。
- **精度评论 + 怎么改**（5）：`bare_rock` **PA=0，完全没分对**——3个验证点全错，直接原因是训练点太少(去重后只有7个独立点，4训练/3验证)，这个类的局限从US1就已经写明，这里是必然结果，不是新问题。改进方向：①gorse_broom/native_scrub这对，可以加入更能区分二者的特征(比如红边指数，本项目Landsat8没有，S2才有，见workflow.md火前必须用L8的局限)；②bare_rock需要想办法多补点(哪怕靠人工数字化)，样本量太小任何分类器都学不好；③可以试试RF回归里筛出来的关键变量(pre_B5/NDVI)加权或做特征选择，减少弱变量干扰。

### R6 流程图（10分 · 喂：US8）
- 放**更新版**流程图（含 §3/§4 统计层，见 US8 的 4 个框）+ 一段 **way forward**（往 A4 最终分类+精度走）。

### R7 地图（4分 · 喂：US6/US7/US9）
- 高质量**分类图** + **refugia 图**；每图查 6 要素（title/legend/scale/north/inset/source+EPSG:2193）。

### R8 时间线（4分 · 喂：US10）
- 更新到 **A4 最终报告 + oral**，每周做什么。
