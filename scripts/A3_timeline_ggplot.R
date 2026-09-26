# ============================================================
# A3_timeline_ggplot.R
# ERST619 Kaupapa Tuhika 3 — Project Timeline (甘特图 / Gantt)
# A3 版：贴合已完成的分析(R3 探索 / R4 关系 / R5 分类 S+Sp)，A3 延期到 09-27，重心前移到 A4。
# 输出: figures/A3_timeline.png
# ============================================================

library(ggplot2)

today <- as.Date("2026-09-26")

# 1) 任务（对应真实做过 + 往 A4 走）/ tasks
tasks <- data.frame(
  task  = c("P0  A2 proposal",
            "P1  Acquire + pre-process Landsat 8 (pre/post-fire)",
            "P2  Feature stack: spectral + 2016 spring (S+Sp); terrain as covariate",
            "P3  Data exploration & cleaning + separability JM  (R3)",
            "P4  Relationships: regression dNBR ~ pre-fire predictors  (R4)",
            "P5  RF classification (S+Sp) + accuracy + refugia  (R5) [Obj 1-2]",
            "P6  Final maps in ArcGIS Pro",
            "P7  Refine classification + accuracy assessment (A4)",
            "P8  Overlay refugia x vegetation x terrain -> species shortlist [Obj 3-4]",
            "P9  Write final report",
            "P10 Prepare & give oral"),
  phase = c("A2","Analysis","Analysis","Analysis","Analysis","A3","A3","A4","A4","A4","Oral"),
  start = as.Date(c("2026-09-07","2026-09-09","2026-09-12","2026-09-15","2026-09-18",
                    "2026-09-20","2026-09-26","2026-09-28","2026-10-05","2026-10-12","2026-10-19")),
  end   = as.Date(c("2026-09-13","2026-09-13","2026-09-16","2026-09-20","2026-09-22",
                    "2026-09-26","2026-09-27","2026-10-06","2026-10-14","2026-10-22","2026-10-25"))
)

# 2) done 标记(结束日 <= today 的算已完成)
tasks$done <- tasks$end <= today

# 3) P0 排最上（ggplot y 由下往上，故 rev）
tasks$task  <- factor(tasks$task, levels = rev(tasks$task))
tasks$phase <- factor(tasks$phase, levels = c("A2","Analysis","A3","A4","Oral"))

# 4) 提交截止日 / milestones（A3 延期到 09-27）
milestones <- data.frame(
  label = c("A2","A3","A4 report"),
  date  = as.Date(c("2026-09-13","2026-09-27","2026-10-23"))
)

ny <- nrow(tasks)

# 5) 画
p <- ggplot(tasks) +
  geom_segment(aes(x = start, xend = end, y = task, yend = task, colour = phase),
               linewidth = 7, lineend = "round") +
  # 已完成任务打个勾
  geom_point(data = subset(tasks, done),
             aes(x = end, y = task), shape = 21, size = 2.6,
             fill = "white", colour = "#3A2A22", stroke = 0.9) +
  # 里程碑虚线
  geom_vline(data = milestones, aes(xintercept = date),
             linetype = "dashed", colour = "#8A756A") +
  geom_text(data = milestones, aes(x = date, y = ny + 0.3, label = label),
            vjust = 0, hjust = 0.5, size = 3, colour = "#4A3A30") +
  scale_colour_manual(values = c("A2"="#D9662B","Analysis"="#E7A33E","A3"="#B5451F","A4"="#8C3A2B","Oral"="#5C4033")) +
  scale_x_date(date_breaks = "1 week", date_labels = "%d %b") +
  scale_y_discrete(expand = expansion(add = c(0.6, 1.6))) +
  labs(title = "ERST619 Kaupapa Tuhika 3 - Project Timeline",
       subtitle = "Port Hills 2017: pre-fire fuel classification (S+Sp) -> ephemeral refugia. Open dot = done.",
       x = NULL, y = NULL, colour = "Phase") +
  theme_minimal(base_size = 11) +
  theme(panel.grid.minor = element_blank(),
        legend.position = "top",
        plot.title = element_text(face = "bold", colour = "#3A2A22"))

ggsave("figures/A3_timeline.png", plot = p, width = 12, height = 5.6, dpi = 300)
cat("已导出 figures/A3_timeline.png\n")
