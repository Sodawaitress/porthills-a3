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

**⚠️ 待检查**：per-class 切分不均，尤其 **gorse_broom train=45/valid=5**，
比2017见过的最不均情况（broadleaf_scrub 58/42）极端得多——valid只有5个点，
后面算混淆矩阵这类会不稳。原因大概率是 gorse_broom 的点在空间上集中在少数几个
300m格子里，随机分格子的时候运气不好全被分到train那边。**下一步该做的**：
要么换个随机种子重切，要么改成分层按类抽格子（保证每类都有格子落到valid）。
现在还没改，先如实记录。

**产出**：`TrainingPoints_2024_raw.shp`（NZTM，含 FuelClass/class_id/split/block_id）、
`TrainingPoints_2024_wgs84.csv`（喂 GEE 特征栈采样用，US2等效步骤）。

---

## 还没做的（US2起，跟2017对齐的下一批）
- 特征栈：Sentinel-2 火前合成 + 指数(NDVI/NBR/BSI/NDRE) + 地形(已有CHM，可以
  直接把冠层高度也当一个特征，不只是拿来定标签——2017没有这个变量)
- 在训练点上采样成点表（US2）
- §3-§5 统计探索/回归/分类流程
- gorse_broom 切分不均这个问题解决掉

## 清理记录（2026-09-21）
- 删除 `07_finalize_cleared_pine_2024.py`（epoch不一致的bug版本，被11号取代，
  留着容易被误跑出错的结果）。
- 删除几个意外落地的临时栅格副产品文件（`Extract_CHM_2021.*`，05号脚本
  `ExtractByMask` 中间结果被 arcpy 自动存盘产生的，非有意产出）。
- 10号脚本末尾原本打印一段用旧的错误数字(538ha版本)做的"完整汇总"，已删除，
  改成指向11号脚本（正确版本）。
