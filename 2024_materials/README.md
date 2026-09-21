# 2024 Port Hills 火 — 方法记录

> 目的：把 2017 那套 US1-US7 全流程在 **2024 Port Hills 火**(2024-02-14 起,Worsleys Rd,
> 官方边界 467.3ha,跟 2017 火场 98.6% 重叠——几乎是原地重烧)上复现一遍，看能不能做得
> 更好、更有意义，最后把两次经验合并成 `methodology_playbook.md` 那套通用流程。
> 脚本按执行顺序编号；**每一步写清楚：目的→做了什么→结果→为什么这么定**，
> 照 `workflow.md` 的"方法记录"体例。**被淘汰/证伪的尝试也留着**，不是失败，
> 是"试过、不行、为什么"的记录，比删掉更有说服力。

---

## 1. 火场边界 + 燃烧强度（`01_dNBR_2024_PortHills.py`／`01b`／`02`）
**谁做的**：另一台机器（这份记录之前）。
**做了什么**：Sentinel-2 SR 火前(2024-01-10~02-13)/火后(02-20~03-31)合成，NBR/dNBR，
USGS severity 分级；边界最终换成 **Environment Canterbury 官方边界**（`boundary/`），
不是最早那份标"Approximate"的 ArcGIS Online 图层。
**结果**：`figures/DNBR_2024_Sentinel2.png`／`SEVERITY_2024_Sentinel2.png`。

---

## 2. CHM 冠层高度（`03_chm_by_lcdb_class.py` → `04_chm_map_and_cleanup.py`）
**目的**：查清"火烧迹地现在长的到底是什么"，而不是只信 LCDB 标签名字
（Yu 提醒：先查实际植被构成再定分类体系，见对话）。
**数据**：`J:\Data\...\CHC_LiDAR_2020_21_{DSM,DEM}.tif`（LINZ 官方"Canterbury -
Christchurch 1m DEM/DSM (2020-2021)"，实测航测日期2020-12-18，验证过在2024火场
AOI内完整覆盖无缺口）。CHM = DSM − DEM。
**踩的坑（03，已修）**：原始 CHM 有 104-143m 的离群值——物理不可能，是陡坡处
DSM/DEM 两次扫描配准误差被放大。**04 里 cap 到 0-40m** 修正，中位数几乎不变
（说明离群值只影响均值，不影响中位数）。
**结果**：按 LCDB Name_2023 分组的中位数高度——**"Exotic Forest"中位数仅0.71m、
"Forest-Harvested"仅0.41m**，完全不是"森林"该有的高度，说明标成森林的地方
大概率是2017火后补种的幼树或未恢复的迹地，不是真乔木层。图见
`figures/CHM_vs_LCDB2023_map.png`。

---

## 3. 用 CHM 高度阈值分 exotic_pine/cleared_pine —— **试过，不行**（`05_chm_threshold_pine_vs_cleared.py`）
**目的**：能不能直接用一个冠层高度阈值，把"真乔木"和"未恢复"分开。
**方法**：k-means(k=2) 在 Exotic Forest+Forest-Harvested 范围(154.5ha)的 CHM 值上跑。
**结果**：**失败，没有干净的自然分界**——k-means 给出"12.97m"完全是被尾部几个
极端像元拽出来的，直方图上根本不是两个山峰，是单峰(90分位数才2.13m)拖一条
几乎看不见的长尾。**放弃这条路**，改用外部验证过的信号（见下一步）。
**图**：`figures/CHM_histogram_pine_threshold.png`（留着当"为什么不这么做"的证据）。

---

## 4. Hansen 森林损失法定义 cleared_pine（`06`/`06b`/`11`）—— 跟 2017 同一套方法
**目的**：2017 项目就是这么定义 cleared_pine 的（Hansen 森林损失 ∩ 松林边界），
这次沿用，只是把单一年份(lossyear==16)扩成年份范围(17-23)，因为这次问的是
"7年里有没有真正恢复过郁闭冠层"，不是"火前一年被砍没砍"。
- `06_hansen_loss_since_2017.js`：GEE Code Editor 版本（浏览器直接跑，不需要本机认证）。
- `06b_hansen_loss_2017_2023_py.py`：Python 版本，实际在 GEE 认证过的机器上跑的，
  输出 `hansen_loss_2017_2023.geojson`（444.9ha / 89 blocks，整个 Port Hills 矩形范围内）。
- `11_fix_cleared_pine_overlap.py`：跟 2023 年 LCDB 的 "Exotic Forest + Forest-Harvested"
  范围(154.5ha)取交集，**不是**跟 2012 年范围（见下面第6步的坑）。

**⚠️ 踩过的坑（已删掉原始脚本 `07_finalize_cleared_pine_2024.py`，别再用）**：
第一版用了 **2012年** LCDB 松林边界(225.5ha)去跟 Hansen 交集，但其余3类
(gorse_broom/pasture/broadleaf_scrub) 用的是 **2023年** 标签——两个时间基准不统一，
导致 LCDB 自己已经把部分原松林地块改判成金雀花的那部分被**算了两次**，5类加总
538.4ha，比 AOI(467.3ha)多了71ha。**11 号脚本修好**：统一用2023年基准重算。

**最终结果**：
- cleared_pine = **122.8 ha**（7 块）
- exotic_pine = **31.7 ha**
- 跟第2步CHM的独立发现方向一致（两种完全不同的方法——结构高度 vs 变化检测——
  互相印证：这片松林绝大部分没有真正恢复）。

---

## 5. bare_rock 候选搜索 —— **负结果，这次不设这个类**（`09_bare_rock_candidates.py`）
**方法**：跟2017同法，坡度>60°连通域搜索。
**结果**：520个连通簇，但绝大多数只有4-30个像元(<0.03ha)，最大的一簇也只有0.176ha，
跟2017（3个确认的海岸悬崖点位）完全不是一回事——这片 AOI（Worsleys Rd）大概率
不靠海岸悬崖，这些碎片更像1m LiDAR在灌丛地形上的噪声。**没有航片核实的情况下，
证据不支持硬凑一个类**。这是合理的地理事实差异，不是方法失败——写进两次经验对比
里：不是所有 Port Hills 子区域都有一样的类别构成。

---

## 6. 其余3类 LCDB 2023 重分类（`10_finalize_remaining_classes.py`）
直接沿用2017 US1.4的分组逻辑：gorse_broom←Gorse/Broom+Manuka/Kanuka，
pasture←High+Low Producing Grassland，broadleaf_scrub←Broadleaved Indigenous
Hardwoods。没有歧义，跟第4步不一样的是这三类从一开始就是2023年基准，不受
第4步那个坑影响。

---

## 7. 最终 5 类方案汇总（面积核对：**467.3 ha = AOI，不多不少**）

| 类别 | 面积(ha) | 占比 |
|---|---|---|
| gorse_broom | 140.7 | 30.1% |
| cleared_pine | 122.8 | 26.3% |
| pasture | 112.8 | 24.1% |
| broadleaf_scrub | 59.3 | 12.7% |
| exotic_pine | 31.7 | 6.8% |

跟 2017 的结构性差异（两次经验对比的关键素材）：
- **cleared_pine 从2017的小补充类(6.7ha)变成第二大类(122.8ha)**——因为这次是
  同一块地原地重烧，"火前燃料"本来就是上次火后的重生植被。
- **bare_rock 直接没有**——这片子区域没有海岸悬崖地形基础。
- **cleared_pine 这次空间上更连片**（7块 vs 2017的4块，且单块更大），
  意味着这次或许能把它**放进分类器里训练**，不用像2017那样只能当已知掩膜用
  （2017排除的原因是太碎、空间分块学不出边界，PA=0.067）——这点等US6跑分类
  时验证。

---

## 8. 训练/验证点撒点（`12_place_training_points.py`）
**参数**：每类50点，最小间距**10m**（对应 Sentinel-2 一整个像元，不是"半个像元"——
之前对话里说错成15m，已纠正；2017的30m规则本来也是**一整个**Landsat像元，不是半个）。
**结果**：250点全部撒够（5类×50，没有因为面积不够撒不满）。
**300m空间分块 70/30 切分**（跟2017同法，避免逐点随机切分导致空间自相关泄漏）：
69个格子，48个→train。

**已修（`13_fix_spatial_split.py`）**：原始随机分格子导致 gorse_broom
train=45/valid=5（比2017见过的最不均情况58/42极端得多）。改成贪心平衡分配——
还是按300m格子整块分（没有放弃"同格子必须同边"这条防泄漏的核心原则），
但格子分给train还是valid时，优先让**每个类**的train占比都逼近70%，不是只看
格子总数的70%。跑了500个随机起始种子选最优，结果**5类全部精确70/30
(35 train / 15 valid)**，比2017任何一版都均匀。

**产出**：`TrainingPoints_2024_raw.shp`（NZTM，含 FuelClass/class_id/split/block_id）、
`TrainingPoints_2024_wgs84.csv`（喂 GEE 特征栈采样用，US2等效步骤）。

---

## 9. 特征栈采样（US2等效，`14_sample_terrain_chm.py` + `15_sample_s2_features.py`）
**地形+CHM（14，本机直接跑完了）**：elevation/slope/northness(=cos(aspect)) +
CHM，直接 `ExtractMultiValuesToPoints` 写到250个点上，250点全部有值(0个空值)。
改用 `ExtractMultiValuesToPoints` 而不是2017的 `arcpy.sa.Sample()`——2017那次
就是 `Sample()` 自动生成的 `OBJECTID` 字段跟真实点ID搞混了，导致过半行标签和
波段值全部对错位（workflow.md US2方法记录有记）；`ExtractMultiValuesToPoints`
直接写回原始要素，没有另外的ID字段可以搞混，从根上绕开这个坑。
输出：`TrainingPoints_2024_terrain.csv`（join key = `FID`）。

**Sentinel-2 光谱+指数（15，需要GEE认证，还没跑）**：火前合成窗口跟01b/02的
dNBR一致(2024-01-10~02-13)，波段=B2/B3/B4/B5/B6/B7/B8/B8A/B11/B12，
指数=NDVI/NBR/NDWI/NDRE/BSI（NDRE是2017没有的——2017火前只有Landsat 8可用
[S2 SR火前还没上线]，红边波段只能靠07/08号脚本事后单独补采样；这次S2从一开始
就是主特征栈的一部分，不用另外补）。**这一步需要在GEE认证过的机器上跑**
（跟06b一样），跑完把 `TrainingPoints_2024_s2.csv` 提交回来，我这边再跟
terrain那份按 `FID` 合并成最终点表。

**S2跑完后的修正（另一台机器做的）**：15号脚本最早用的火前窗口(2024-01-10~02-13)
跟dNBR脚本(01b)一样紧，结果只有2景可用，**130/250点落进云洞**。dNBR要紧窗口是
为了准确对齐火烧前后，但特征栈只要"干净的火前植被特征"，不需要跟火贴那么近——
**放宽到2023-12-01起（4景），250/250点全部采到**，仍在火前同一个夏季里。
这条经验值得记进通用流程：**同一个AOI，不同用途的合成窗口不必用同一个**。

## 10. 合并成最终点表（US2完成，`16_merge_point_table.py`）
地形+CHM表（14号，250行）跟S2光谱+指数表（15号，250行，FID完全对齐、无缺失）
按 `FID` 合并。**产出：`PortHills2024_PointTable.csv`，250行×24列**
（FuelClass/class_id/split/block_id + elev/slope/northness/chm + 10个S2波段
+ NDVI/NBR/NDWI/NDRE/BSI），5类全部 35train/15valid——US1+US2 等效流程完成，
跟2017的 `PortHills_PointTable.csv` 是同一个角色。

## 11. §3 First Pass（`17_s3_exploration_pass1.py`，踩坑已修 `18_fix_edge_slope_northness.py`）
**空值/常数列/重复行**：全部干净(0个)。
**⚠️ 踩过的坑（已修）**：箱线图里 `slope`/`northness` 两列被一个 **-9999** 离群值拉爆
y轴，249个点全挤成一条线看不出来——查出是2个点(FID 105/118，都是exotic_pine)的真实
问题：**坡度/坡向需要3×3邻域算梯度，这两个点离AOI边界太近，靠外侧的邻居像元在DEM
裁剪时被切掉了**，导致slope/aspect算不出来（但elev/chm不需要邻域，同样两个点这两列
是正常的，说明问题precisely在"需不需要邻域"这条线上）。**修法**：DEM先按AOI**外扩
100m**裁剪、在这个更大的范围上算slope/aspect/northness，再只在这两个点上重新取值——
不用像2017那样直接删点，250点一个没少。
**IQR离群值**：chm最多(31个，跟已知的强右偏分布一致)，光谱波段普遍个位数到十位数，
地形三兄弟(elev/slope/northness)修完之后都是0。
图：`exploration/boxplots_by_class_2024.png`。

## 12. §3 Second Pass + 两个真数据问题（`19_s3_normality_by_class.py` → `20`/PID修复）
**正态性**：19/95(类,变量)组合非正态(5类×19变量)。`chm`**全部5类都非正态**(右偏，
符合"大部分近地表+少数真乔木"的已知结构)；`pasture`最广(10/19变量)。

**⚠️ 踩过的坑1——真实LiDAR数据空洞（已修）**：追查pasture的elev离群值时，发现
3个点(pasture) elev=slope=northness=chm**全部精确为0**，同时NDVI等S2波段完全正常
(~0.83-0.86，健康植被)。核实用**原始未裁剪**的DEM/DSM直接在该坐标查值，DEM和DSM
两个都是0——不是裁剪边界效应（那是上一步slope/northness的坑），是**这片LiDAR本身
就有数据空洞**。回查全表又发现同样问题在exotic_pine还有4个点，7个点全部聚在同一块
约270m×290m的小范围内(NZTM x:1569560-1569825, y:5169520-5169810)——不是随机分布，
是真实的局部覆盖缺口。**处理**：删掉这7点（跟2017遇到真数据缺口时的处理原则一样：
真缺口就删+如实记录，不硬凑），pasture降到47点、exotic_pine降到46点，其余3类仍50。

**⚠️ 踩过的坑2——我自己造成的ID对不上（已修，比坑1更值得记）**：删完7点后用
shapefile的`FID`字段去同步`TrainingPoints_2024_terrain.csv`——**shapefile删行后
FID会自动从0重新连续编号**，不是保留原编号，导致同步时把错的FuelClass/split值
写到了错的行上（cleared_pine从50变成"57"这种荒谬数字就是这么来的）。**这正是
`ExtractMultiValuesToPoints`那条经验想防的同一类坑，但这次是我自己在别的地方
(手动同步脚本)又踩了一遍**——教训是这条规则不能只用在"选哪个采样工具"上，
**任何时候只要shapefile可能被删过行，都不能再拿它的`FID`当跨文件的join key**。
**修法**：加了一个手动赋值、之后再也不会被自动重编号的**`PID`字段**（0-242，
一次性赋值），所有CSV(terrain/wgs84)重新按`PID`导出；`15_sample_s2_features.py`
和`16_merge_point_table.py`都已改成认`PID`不认`FID`。**S2那份需要重新在GEE机器
上跑一次**(15号脚本)，因为S2数据是按旧的FID编号采的，现在对不上了。

**PID修复+S2重采样已完成**（另一台机器跑的）：243点，terrain+S2完全对齐，0缺失。
最终每类：broadleaf_scrub 35/15、cleared_pine 35/15、exotic_pine 32/14(46)、
gorse_broom 35/15、pasture 33/14(47)——跟坑修好之前script 13算出的数字完全一致，
确认PID方案是对的。**US1+US2等效流程 + §3两遍探索，全部完成，数据干净。**

## 13. §3 变换测试（`21_s3_test_transforms.py`）
先拿掉3个坏点重跑了一遍19号脚本——**pasture/elev不再非正态**（之前的偏度峰度
是那3个错误的0值撑出来的，删完数据本身就正常了，两条独立诊断(First pass离群值
+ Second pass正态性)都指向同一个数据问题，互相印证）。19/95组合仍非正态，
`chm`还是最普遍(5/5类都中)。

**log变换对chm效果非常干净**，5类全部从非正态变正态：
| 类别 | skew(raw→log) | kurt(raw→log) |
|---|---|---|
| cleared_pine | 4.907→**0.261** | 24.515→**0.605** |
| broadleaf_scrub | 2.224→**0.293** | 4.968→**-1.014** |
| gorse_broom | 2.141→**0.353** | 3.550→**-0.532** |
| exotic_pine | 1.308→**0.553** | 0.029→**-1.125** |
| pasture | 1.453→**-0.112** | 1.467→**-1.198** |

**exotic_pine的northness(现在最差，skew=-3.08/kurt=9.27)测过log/sqrt——跳过**：
northness取值-1到1，有负值，log/sqrt都不能直接用；z-score不改变形状（只是sanity
check）。**如实记：这个非正态留着，不是没测就放弃**——northness本身是方向性变量
(cos值)，天生就不是拿来做line性回归假设的那种连续量，RF(不要求正态)不受影响，
主要影响§4回归，报告里可以说清楚这条限制。

## 14. 火后 dNBR 采样（US4等效前置）+ SCL 烧痕误判修复（`22`/`22b`/`22c`/`23`）
**目的**：在243个训练点上采火后S2、算dNBR，喂§4回归（跟2017用dNBR连续值当Y同法）。
**第一版的大坑**：22原版（火前窗2024-01-10紧 + 火后SCL掩云影class3）只有**117/243**有效，
126点丢，pasture最惨12/47。
**试过、不行——B(延窗)**（`22b`）：火后窗延到04-30/05-31，**一个点没救回**(还是117)，只把
已有点dNBR越拖越偏（中位偏移-91→-142，大到能改严重度等级）——正是2017记过的火后植被恢复
偏差重演。证伪，别延窗。
**病根（`22c`确认）**：126个丢点全在AOI内、跟有效点交错，不是地理问题。真凶=**SCL把深色烧痕
误判成"云影"(class 3)掩掉**。火后只掩真云(8/9/10)、保留云影，**+65点回来**(117→182)，救回的
正是烧最狠的类(broadleaf_scrub+20/gorse_broom+18/pasture+12)。
**眼见为实（`23`，图`exploration/truecolor_burn_vs_cloud.png`）**：左=真彩(2024-03-03最干净景，
11%云)，训练点全压在暗红褐烧疤上、不是白云；右="整个火后窗SCL判云影的频率"热图，烧疤位置
整片烧红=被反复误判。像素级铁证，回答"到底是云还是烧焦"。
**最终修法（两处，`22`已改）**：①火前窗放宽到2023-12-01（对齐15，火前夏季植被稳定；原来那65点
其实卡在火前云洞，不是火后问题）②火后掩膜只掩真云8/9/10、保留云影=烧痕。→ **243/243全覆盖，
零时间偏差，烧痕样本一个不丢**。产出`TrainingPoints_2024_dnbr.csv`（243行，post波段+NBR_pre/post+dNBR）。
**⚠️留给2017（等2024全跑完一起搞，别现在动主报告）**：2017同一个坑——`scripts/01_build_point_table.py`
`10`/`11` 的 `QA_PIXEL` 掩膜都掩了 `1<<4`=云影，深色烧痕同样会被误杀（那16个被当"云洞"丢的
cleared_pine点很可能有一批是烧痕）。Landsat CFMask通常比S2 SCL温和，影响可能更小，**待量化**。
记在 `product.md` 🟡 表。

---

## 还没做的（跟2017对齐的下一批：§4-§5）
- §4 关系（相关表+VIF、dNBR回归——这次dNBR/火后波段还没采样，也可以直接把
  Spearman(F1)并进去一起跑，不用像2017分两次）
- §5 分类（JM可分性 → RF，cleared_pine这次更连片，或许能直接进分类器）
- §4 关系（相关表/VIF清理 → dNBR回归）—— 2024这次dNBR/火后波段还没采样，
  需要先决定Y变量怎么来（跟2017一样用dNBR连续值，还是这次有别的想法）
- §5 分类（JM可分性 → RF → 混淆矩阵）——这次cleared_pine更连片(7块非2017的
  4块)，见第7步笔记，或许能直接进分类器训练，不用只当掩膜

## 清理记录（2026-09-21）
- 删除 `07_finalize_cleared_pine_2024.py`（epoch不一致的bug版本，被11号取代，
  留着容易被误跑出错的结果）。
- 删除几个意外落地的临时栅格副产品文件（`Extract_CHM_2021.*`，05号脚本
  `ExtractByMask` 中间结果被 arcpy 自动存盘产生的，非有意产出）。
- 10号脚本末尾原本打印一段用旧的错误数字(538ha版本)做的"完整汇总"，已删除，
  改成指向11号脚本（正确版本）。
