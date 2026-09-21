# 2017 报告完善清单 · A1 资产 + 2024 方法整合
> 2026-09-21 建。把 **A1 已做对的探索** + **2024 复现挖到、可用于 2017 的方法** 合成一份，
> 用来把 A3 的 2017 报告做到完美。一处真相：细节在 `references.md`/`product.md`，这里是主索引。

## 0. 核心认知（先看这个，别再走弯路）
- **A1 你做得又对又惊艳，只是没写进报告正文。** Helen 批注：方法/脚本 **8/10**，写作/解释 **0–4/10**。
  **53/100 全丢在"没解释、没引用、难读"，不是方法错。** 她原话："this work to check pre-fire NBR is 0
  and control for elevation, slope is good — **why didn't you mention it in your report?**"
- **✅ 已核实：A3 点表 dNBR 用的就是 A1 的智能掩膜**——pasture 44/44、各类都齐（只有 cleared_pine 3/19
  是真云洞）。**2017 主表没有烧痕 bug。** （之前 `scripts/12_test_shadow_burnscar_2017.py` 用的是从没
  用过的 naive 掩膜，+32 是假警报，作废；那脚本留作"证明 A1 掩膜是对的"的反面对照。）
- **所以"完善 2017" = 把 A1 已做对的技术活在报告里讲清楚（做什么+为什么+引用）+ 补 2024 的方法层。**
  不是重做，是**揭示 + 加深**。

## 1. A1 已有的惊艳资产（👤 Yu 自己的活 → 报告里当"本研究方法/发现"，不当文献引）
| A1 资产 | 是什么 | 进 A3 哪节 | 为什么值钱 / Helen 怎么说 |
|---|---|---|---|
| **烧痕≠shadow 智能掩膜** | 云(bit3)到处掩；云影(bit4)**只掩火场外、火场内保留=烧痕**；量化 **242 ha** 高 dNBR 地被误当 shadow | §3 清洗 + §5/§6 limitation | 教科书级。**A3 要正面展示"是烧痕不是 shadow"**（配真彩图，见 §5 落地） |
| **offset 校正** | 控制环(2km−500m)按 elev/slope/覆盖类型匹配火场 + Dynamic World **排除作物**(割过的牧草像烧过) + 排水体；`dNBR−offset` | §3 outlier + §4 | **Helen 点名 praise**。正好解释那个 outlier：未烧植被 dNBR 本应=0 却是 **120.5** |
| **阈值 = 未烧岛 p90 + 否决 Otsu** | 用两个手绘未烧岛的 dNBR p90 当阈值；试过 Otsu 但"cut inside burned group"故弃 | §7 refugia 定义 | 严谨模型选择，比"severity==0"更有据 |
| **岛屿验证** | 手绘岛=独立参照，算 recall / mean dNBR / covered ha | §5/§7 精度 | 独立参照的合理性检查 |
| **未制图 refugia 发现** | 算出官方手绘图**漏掉**的未烧区(我的未烧 − 官方岛) | §7 结果 | 真发现，直答 refugia 科学问题 |
| **统计表** | pre/post/change 各波段 + **NBR 0.583→0.101**(−0.482) | §3 统计 | 清晰的燃烧光谱签名 |
| **波段组合 + NDVI + BSI** | 自然色/CIR/**SWIR 烧痕组合** + NDVI(veg mask) + BSI(裸土独立核查) | §3 可视化 | Helen: "**why don't you present your NDVI and BSI?**" |
| **paddock/harvest 洞见** | 宽视野里矩形斑=割过的牧草不是火 → **dNBR 测的是植被移除不是燃烧** | §5 cleared_pine 起源 + §6 limitation | cleared_pine 这条线的源头 |
| **northness 不用 aspect** | 环形量：359°和1°数值差358但方向近 → 取 cos | §4 地形 | 正确处理环形变量 |

## 2. 2024 研究挖到、可用于 2017 的方法层（📖 可引文献）
| 方法 | 进 A3 哪节 | 状态 | 出处(references.md) |
|---|---|---|---|
| Spearman 秩相关 | §4 相关 | ✅已做 `04e` | E3 Domingo2020 (F1) |
| **RBR vs A1 offset**（见 §3 决定点） | §4 Y 变量 | 决定点 | C 组 Parks2014 |
| **SHAP** 变量重要性 | §5 | 加 | D 组 Lundberg&Lee2017 |
| F2–F5 引用背书 | §3/§5 | 加 | E2/E3 |
| 树>DL（justify RF 不用 CNN） | §5 | 写理由 | D 组 Grinsztajn2022 |
| Satellite Embedding | **A4**（不在 2017） | 未来 | D 组 AlphaEarth |

## 3. 一个决定点：RBR 换掉 A1 的 offset？还是并存？
- **A1 已做 offset 校正**（减控制环均值）——处理**季节/大气漂移**，是 Yu 自己的、Helen praise 过的亮点。
- **RBR**（Parks）——**除以 pre-NBR**，处理**火前生物量偏差**。两者解决**不同**问题。
- **建议**：**保留 A1 的 offset（你自己的亮点，务必讲清楚）**，§4 再**并列报一版 RBR** 当 SOTA 对照
  （引 Parks2014）。不是二选一把 A1 的活删掉。**你定。**

## 4. Helen A1 反馈 → A3 写作红线（全项目通用，最要命）
- 每个技术动作都要**"做了什么 + 为什么"写进正文**，不能只躺在脚本注释里。
- 每个论断**挂引用**。
- 方法是好的 → 报告的任务是**"揭示"它们**（"your writing does not reveal your technical abilities"）。

## 5. 落地顺序（一次一块，句子你自己写）
1. **§3**：把 A1 的 掩膜 / offset / 统计表 / NDVI+BSI 写成正文（做什么+为什么+引用）；
   **正面展示"烧痕不是 shadow"**——配一张 2017 真彩+云影频率图（照 2024 `23` 脚本改，那张已验证有效）。
2. **§4**：Spearman(已做) + **RBR 对照** + VIF + 回归结果解释 + **SHAP** 变量重要性。
3. **§7**：用 A1 的**岛屿 p90 阈值** + **未制图 refugia 发现** + 岛屿验证。
4. **全程补引用**，对齐 Helen 三条红线。
