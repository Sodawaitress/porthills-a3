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
- **正态性**（5）：哪些波段 **skew>|1| / kurt>|2|** = 非正态？列出来下结论。
- **变换**（5）：试了哪个（log/sqrt/标准化）、为什么、改善没；**若不做 → 为什么不做**（挂"RF 尺度不变"）。

### R4 关系（25分 · 喂：US4）
- **相关表**（5）：哪些变量和 field 最相关？有没有冗余（>0.8）。
- **散点**（5）：关系什么形状（线性/非线性）。
- **哪种回归 + 为什么**（5）：dNBR 当连续 Y → 线性回归；说清为什么这么选。
- **结果 + 解读 + 挂 3 文献**（5）：报 R²/RMSE，讲成故事。
- **精度评论**（5）：多准、什么问题、怎么改。
- ⭐ 别忘写**多重共线性/VIF**（你波段+指数高度相关）。

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
- **可分性**（5）：JM 指数 + 光谱曲线，类分得开吗。
- **像元/对象 + 为什么**（2）；**算法 RF + 为什么 + 引用**（5）。
- **结果 + 混淆矩阵解读 + 挂文献**（5）；**精度评论 + 怎么改**（5）。

### R6 流程图（10分 · 喂：US8）
- 放**更新版**流程图（含 §3/§4 统计层，见 US8 的 4 个框）+ 一段 **way forward**（往 A4 最终分类+精度走）。

### R7 地图（4分 · 喂：US6/US7/US9）
- 高质量**分类图** + **refugia 图**；每图查 6 要素（title/legend/scale/north/inset/source+EPSG:2193）。

### R8 时间线（4分 · 喂：US10）
- 更新到 **A4 最终报告 + oral**，每周做什么。
