# ============================================================
# 04_A3_cleaning_funnel.R
# ERST619 Kaupapa Tuhika 3 — Spatial data cleaning funnel
# 每一步清洗后研究区还剩多少面积 (ha)
# 数字来源：PortHills2017_stackA3.tif (31 bands, 30 m NZTM grid)
#   每个格子 = 30 x 30 m = 0.09 ha
# ============================================================

library(ggplot2)

# 1) 清洗步骤 / cleaning steps ------------------------------
#    ha     = 该步之后剩下的面积
#    branch = 这一层给谁用
#    note   = 这一步去掉了什么、为什么
steps <- data.frame(
  step   = c("1  Official fire perimeter",
             "2  All 30 m cells touching the perimeter",
             "3  Interior cells only (inside_aoi = 1)",
             "4  + Cloud-free post-fire (dnbr_data = 1)",
             "5  + No negative post-fire reflectance (post_neg_refl = 0)"),
  ha     = c(1758.88, 1849.32, 1672.29, 1501.47, 1372.68),
  branch = c("Reference", "Grid", "Vegetation classification",
             "dNBR / refugia", "dNBR / refugia"),
  note   = c("CDEM/ECan fire boundary + 2 unburnt islands filled",
             "partial edge cells counted as whole cells",
             "removed 1,967 mixed edge cells (177.0 ha)",
             "removed post-fire cloud gap (170.8 ha)",
             "flag, don't delete: dark-char cells (see note below)")
)

# 2) 顺序与标签 ---------------------------------------------
#    ggplot 的 y 轴由下往上画，所以 rev() 让第 1 步排在最上面
steps$step   <- factor(steps$step, levels = rev(steps$step))
steps$branch <- factor(steps$branch,
                       levels = c("Reference", "Grid",
                                  "Vegetation classification", "dNBR / refugia"))
#    百分比都相对官方 perimeter
steps$pct   <- steps$ha / 1758.88 * 100
steps$label <- sprintf("%.1f ha  (%.0f%%)", steps$ha, steps$pct)

# 3) 画 -----------------------------------------------------
p <- ggplot(steps, aes(x = ha, y = step, fill = branch)) +
  geom_col(width = 0.65) +
  # 条形右边：面积和百分比
  geom_text(aes(label = label), hjust = -0.05, size = 3.3, colour = "#3A2A22") +
  # 条形里面：这一步去掉了什么
  geom_text(aes(x = 25, label = note), hjust = 0, size = 3, colour = "white") +
  # 虚线 = 官方面积，方便看每一步比官方多或少
  geom_vline(xintercept = 1758.88, linetype = "dashed", colour = "#8A756A") +
  scale_fill_manual(values = c("Reference"                 = "#8A756A",
                               "Grid"                      = "#B5651D",
                               "Vegetation classification" = "#B5451F",
                               "dNBR / refugia"            = "#8C3A2B")) +
  scale_x_continuous(limits = c(0, 2300), expand = c(0, 0)) +
  labs(title    = "Spatial data cleaning: area retained at each step",
       subtitle = "Port Hills 2017 fire, 30 m NZTM grid (EPSG:2193); % relative to step 1",
       caption  = paste0(
         "Step 1 sums the CDEM/ECan fire boundary WITH the 2 unburnt islands filled in, so it exceeds the official final area (CCC 1,645 ha; AIDR 1,661 ha). Source date to confirm on ECan download metadata.\n",
         "Step 5: dark-char (negative-reflectance) cells are the MOST severely burnt ground — removing them biases burned area & severity LOW, so they are flagged, not deleted.\n",
         "Vegetation classification uses pre-fire imagery only and is unaffected by steps 4-5."),
       x = "Area (ha)", y = NULL, fill = NULL) +
  theme_minimal(base_size = 11) +
  theme(panel.grid.minor   = element_blank(),
        panel.grid.major.y = element_blank(),
        legend.position    = "top",
        plot.title         = element_text(face = "bold", colour = "#3A2A22"),
        plot.caption       = element_text(hjust = 0, colour = "#6b5a50", size = 7.5))

# 4) 导出 ---------------------------------------------------
dir.create("figures", showWarnings = FALSE)
ggsave("figures/A3_cleaning_funnel.png", plot = p, width = 10, height = 5.3, dpi = 300)
cat("已导出 figures/A3_cleaning_funnel.png\n")
