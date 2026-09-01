# Reproducible statistical inference for the landing-page A/B test.

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(ggplot2)
})

# Determine the repository root from the location of this script.
args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) != 1) {
  stop("Could not determine the R script location.")
}

script_path <- normalizePath(
  sub("^--file=", "", file_arg),
  winslash = "/",
  mustWork = TRUE
)

project_root <- dirname(dirname(script_path))

group_path <- file.path(project_root, "outputs", "group_summary.csv")
daily_path <- file.path(project_root, "outputs", "daily_conversion.csv")
figures_dir <- file.path(project_root, "outputs", "figures")
result_path <- file.path(project_root, "outputs", "statistical_test.csv")

if (!file.exists(group_path)) {
  stop("Missing outputs/group_summary.csv. Run Phase 4 first.")
}

if (!file.exists(daily_path)) {
  stop("Missing outputs/daily_conversion.csv. Run Phase 4 first.")
}

dir.create(figures_dir, recursive = TRUE, showWarnings = FALSE)

# Read Phase 4 analytical outputs.
group_summary <- read_csv(group_path, show_col_types = FALSE)
daily_conversion <- read_csv(daily_path, show_col_types = FALSE)

# Validate the group-summary contract.
required_group_columns <- c(
  "group",
  "users",
  "conversions",
  "conversion_rate"
)

if (!identical(names(group_summary), required_group_columns)) {
  stop("Unexpected group_summary.csv schema.")
}

if (nrow(group_summary) != 2) {
  stop("Expected exactly two experiment groups.")
}

if (!setequal(group_summary$group, c("control", "treatment"))) {
  stop("Expected control and treatment groups.")
}

if (any(group_summary$users <= 0)) {
  stop("Experiment-group user counts must be positive.")
}

if (any(group_summary$conversions < 0)) {
  stop("Conversion counts cannot be negative.")
}

if (any(group_summary$conversions > group_summary$users)) {
  stop("Conversions cannot exceed user counts.")
}

if (any(group_summary$conversion_rate < 0 |
        group_summary$conversion_rate > 1)) {
  stop("Conversion rates must be between 0 and 1.")
}

# Extract the two experiment arms explicitly.
control <- group_summary %>%
  filter(group == "control")

treatment <- group_summary %>%
  filter(group == "treatment")

control_users <- as.numeric(control$users)
treatment_users <- as.numeric(treatment$users)

control_conversions <- as.numeric(control$conversions)
treatment_conversions <- as.numeric(treatment$conversions)

control_rate <- control_conversions / control_users
treatment_rate <- treatment_conversions / treatment_users

# Define the effect consistently as treatment minus control.
difference <- treatment_rate - control_rate

# Two-sided two-sample test for equality of proportions.
# Continuity correction is disabled so the result corresponds to the
# standard large-sample two-proportion test.
test_result <- prop.test(
  x = c(treatment_conversions, control_conversions),
  n = c(treatment_users, control_users),
  alternative = "two.sided",
  conf.level = 0.95,
  correct = FALSE
)

alpha <- 0.05
p_value <- unname(test_result$p.value)
ci_lower <- unname(test_result$conf.int[1])
ci_upper <- unname(test_result$conf.int[2])

reject_h0 <- p_value < alpha

decision <- if (reject_h0) {
  "Reject H0"
} else {
  "Fail to reject H0"
}

# Save a one-row machine-readable statistical result.
statistical_result <- tibble(
  control_users = control_users,
  treatment_users = treatment_users,
  control_conversions = control_conversions,
  treatment_conversions = treatment_conversions,
  control_rate = control_rate,
  treatment_rate = treatment_rate,
  difference = difference,
  difference_percentage_points = difference * 100,
  p_value = p_value,
  confidence_level = 0.95,
  ci_lower = ci_lower,
  ci_upper = ci_upper,
  alpha = alpha,
  decision = decision
)

write_csv(statistical_result, result_path)

# Overall conversion-rate figure.
overall_plot <- group_summary %>%
  mutate(
    group = factor(group, levels = c("control", "treatment")),
    conversion_percent = conversion_rate * 100
  ) %>%
  ggplot(aes(x = group, y = conversion_percent, fill = group)) +
  geom_col(width = 0.65, show.legend = FALSE) +
  geom_text(
    aes(label = sprintf("%.2f%%", conversion_percent)),
    vjust = -0.4
  ) +
  labs(
    title = "Overall A/B Test Conversion Rates",
    x = "Experiment group",
    y = "Conversion rate (%)"
  ) +
  theme_minimal()

ggsave(
  filename = file.path(figures_dir, "conversion_rates.png"),
  plot = overall_plot,
  width = 7,
  height = 5,
  dpi = 150
)

# Daily conversion-rate figure.
daily_plot <- daily_conversion %>%
  mutate(
    experiment_date = as.Date(experiment_date),
    conversion_percent = conversion_rate * 100
  ) %>%
  ggplot(
    aes(
      x = experiment_date,
      y = conversion_percent,
      color = group,
      group = group
    )
  ) +
  geom_line(linewidth = 0.7) +
  geom_point(size = 1.3) +
  labs(
    title = "Daily A/B Test Conversion Rates",
    x = "Experiment date",
    y = "Conversion rate (%)",
    color = "Group"
  ) +
  theme_minimal()

ggsave(
  filename = file.path(figures_dir, "daily_conversion.png"),
  plot = daily_plot,
  width = 9,
  height = 5,
  dpi = 150
)

# Print a concise statistical report.
cat("Phase 5 statistical analysis completed successfully.\n")
cat("\n")
cat(sprintf("Control:   %d / %d = %.6f%%\n",
            control_conversions, control_users, control_rate * 100))
cat(sprintf("Treatment: %d / %d = %.6f%%\n",
            treatment_conversions, treatment_users, treatment_rate * 100))
cat("\n")
cat(sprintf("Treatment - control: %.6f percentage points\n",
            difference * 100))
cat(sprintf("p-value: %.10f\n", p_value))
cat(sprintf("95%% CI: [%.6f, %.6f] percentage points\n",
            ci_lower * 100, ci_upper * 100))
cat(sprintf("alpha: %.2f\n", alpha))
cat(sprintf("Decision: %s\n", decision))
cat("\n")
cat(sprintf("Statistical output: %s\n", result_path))
cat(sprintf("Figures directory: %s\n", figures_dir))
