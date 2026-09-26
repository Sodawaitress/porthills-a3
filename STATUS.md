# A3 当前状态 · 交接说明（handoff）

> 给另一台电脑用：打开就知道现在走到哪、哪些东西不在 git 里。
> 更新：2026-09-26

## 一句话
A3 分析全部做完，**主模型定为 S+Sp**。报告 docx 已修好格式 + 应用 Diana 修订。只剩 ArcGIS 两张地图的手动收尾（09-26 下午做）。A3 已延期到 **09-27**。

---

## 主模型决定（R5）
- 4 类 RF：pasture / gorse_broom / broadleaf_scrub / exotic_pine
- 变量集 = **S+Sp**（火前光谱 10 + 2016 春季 9）；**地形不进分类器**，只当 refugia 分析的协变量
- 证据：`R5_shap_run/07_compare_varsets.py`，10 种子空间 CV：S 0.598 / S+T 0.617 / **S+Sp 0.642** / S+T+Sp 0.645 → 春季真金、地形白加、选 S+Sp（同样准就选简单的，还消掉两条 provenance 红旗）
- 最终数字：**CV OA 64.3% ± 2%**，独立测试 **59.1%**（95% CI 49–69）。掩膜发现：荆豆 406→382ha、OID 10049 是标签错。
- SHAP：`06_shap_local.py` → `R5_shap_run/R5_shap/`（图+表）

## 报告 docx ⚠️ 不在 git（`*.docx` 被 .gitignore 排除）
- 文件：`Kaupapa Tuhika 3.docx`（本机 `Desktop/ERST619/A3/`）
- 已做：全文 **Calibri 11**；标题层级理顺（主节 H1 16pt / 子节 H2 13pt，标题 20pt）；**Diana（署名 Daniel King）13 处修订全部应用**；批注忽略
- 备份：`Kaupapa Tuhika 3_BACKUP_1451.docx`
- 元数据没留外部编辑痕迹（creator / lastModifiedBy 仍是 hooper white）
- **另一台要用 → 走 OneDrive/邮件传，git 拿不到**
- 待办：删 3 条残留批注；蓝色孤儿行 "spatial data cleaning" 待定去留；literal `<sub>…</sub>` 标记待转真下标

## R6 流程图 / R8 时间线
- `figures/fig_workflow_A3.gv` + `.png`（含 §3 统计层、§4 关系、S+Sp、cleared_pine 掩膜；A2 原图没动）
- `figures/A3_timeline.png`（源 `scripts/A3_timeline_ggplot.R`；A3 里程碑 09-27，含 today 线）

## ArcGIS 地图 ✅ 已定稿（2026-09-26）
- **三张最终图**在 `exploration/map_final/`：Map1 燃料分类(V2)、Map2 烧毁程度+refugia、Map3 30m格清洗；变体在 `exploration/map_variants/`
- 脚本：`scripts/44_build_all_maps.py`(全自动重建所有 Layout) + `45_build_cleaning_map.py`(Map3)
- 全部按老师布局反馈排(主图左、inset/图例/比例尺/N 竖排右侧左对齐)，三张风格统一
- **跨机找文件看 [`WHERE_IS_EVERYTHING.md`](WHERE_IS_EVERYTHING.md)**（aprx/gdb/大文件在 OneDrive，git 只有 PNG）
- ⚠️ 更正：旧稿"arcpy.mp 没有 `createTextElement`"是**错的**——3.6.1 有，挂 project 对象上；44 号脚本标题/来源全自动生成
- 剩：Map1 定稿选 V3_Confidence / V2_CVDsafe；图题写进 Word（图下方，"Figure X" 加粗）

## 不在 git 的东西（都要另传）
`*.tif`（`PortHills2017_stackA3.tif`、`figures/*.tif`…）、`*.zip`（`classification.zip`、`R5.zip` 内含最终表/图）、`*.pdf`、`*.docx` —— 全被 .gitignore，需 OneDrive/U 盘另传。

## 关键文件索引
- `report.md` — R1–R8 写作提纲 + 中文提示（已更到 S+Sp）
- `report_provenance_S5_S6.md` — 每句出处标记（📖外部/👤Yu/🤖脚本/🤝合推）
- `06_shap_local.py`、`R5_shap_run/` — SHAP + 四套变量集对比
