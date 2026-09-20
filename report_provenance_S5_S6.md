# §5 / §6 写作骨架 · 每句挂出处（写正文对着它）

> 📖外部(可引用) · 👤Yu的决定 · 🤖Claude算的 · 🤝你我从资料推的 · ⚠️查不出=幻疑，重查或删。
> **红线**：👤🤖🤝 = 本研究的东西，写成"发现/方法/决定"，**不当文献引**；只有 📖 配 citation。
> 英文你自己写；这里给的是"每句说什么 + 该不该带引用"。

---

## §5 分类 (27 分)

### 5.1 训练/验证数据
- 6 类：pasture/gorse_broom/exotic_pine/broadleaf_scrub/bare_rock/cleared_pine — 👤 你的类体系
- 按**易燃性**归类(manuka→gorse_broom, 阔叶→broadleaf_scrub) — 👤 决定，理由挂 📖 **Wyse 2016**
- 类源：LCDB **Class_2012** reclass + 2015 航拍核验 — 🤝（LCDB 📖 + 你的 reclass 👤）
- 无火前 field data → 用 reference imagery 当 proxy — 👤 决定 + 📖（简报明说允许）
- **cleared_pine 用 Hansen 2016 森林损失定义** — 🤝（Hansen 📖 Hansen et al. 2013 + 我们的方法）
- 点数：~290(4主类扩样后), bare_rock 仅 7 — 🤖（数据，挂点表）
- 70/30 **空间分块** — 👤 决定 + 📖（Olofsson 2014；空间自相关 ⚠️Ploton 确切引待核）

### 5.2 可分性
- JM=1.46 → gorse/broadleaf **混淆** — 🤖（US5 算的）
- S2 **red-edge NDVI d=0.92**(强)、花期黄度 d=0.61 分离这对 — 🤖（07/08 算的）
- JM/可分性方法 — 📖 Richards 2013 ⚠️版次/页待核

### 5.3 像元/对象 + 算法
- 像元-based — 👤 决定（给一句理由）
- **RF**（少样本稳、给变量重要性、非 DL）— 👤 理由 + 📖 **Christ 2025**（RF+refugia 先例）

### 5.4 结果 + 精度
- 4 类 **OA=0.684, Kappa=0.579** — 🤖（你 arcpy 06c 的官方数字）
- 全图面积：pasture~2400/gorse~1070/pine~790/broadleaf~760 ha — 🤖 ⚠️**以你 arcpy 12 官方为准**（我等价版数字接近）
- **refugia% 按类**：gorse/pine 最低(~5%)、broadleaf/pasture 较高(~10%) — 🤝 ⚠️**用 arcpy 13 官方数字**；我等价版方向一致(gorse 少 refugia)，数值以官方为准
- 结果**印证 Wyse 易燃性排名**(gorse 最燃→最少 refugia) — 🤝（我们的发现，挂 📖 Wyse 佐证）

### 5.5 精度评论 / 问题 / 改进
- gorse/broadleaf 混淆拉低 OA — 🤖
- red-edge(d=0.92)能解 → **A4 加 S2 red-edge** — 🤖 + 计划🤝
- ⚠️ **dNBR 可能高估 pasture refugia**（草地低烈度火被当未烧）— 🤝（我们推的）
- ⚠️ **地形 t 检验 p 值无效**（像元伪重复/空间自相关）→ 只报方向 — 🤝
- ⚠️ 地形进了分类器 vs 原"spectral-only"计划不一致 — 🤝（要么统一说法要么移出）

---

## §6 流程图 + way forward (10 分)
- 更新版流程图（含 §3 探索层 + §4 关系层 + Hansen 支线）— 🤖/🤝（我们建的，改 `refine/fig_workflow.dot`）
- way forward：① A4 加 S2 red-edge 解 gorse/broadleaf ② 补更多火前影像填云洞 ③ 扩验证样本(现 bare_rock 仅 7) ④ 2024 火做跨年对比(⚠️同卫星原则) — 🤝

---

## ⚠️ 当前"查不出/待核"清单（用前必查，否则删）
1. Ploton 等"空间自相关"确切作者/年/DOI — report.md R5 有链接，⏳核
2. Richards 2013 版次/页（JM）⏳
3. gorse 卫星制图那篇确切作者/年（08 脚本 researchgate 230694091）⏳
4. refugia%/面积**官方数值** = 以你 arcpy 12/13 输出为准（我给的是等价版估计）
5. B2/B3 数据源(NIWA/Scion)确切作者年份 — references.md 标 ⏳
