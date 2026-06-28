// Shared Recharts theme so chart palette and tooltip style live in one place.
// Recharts needs literal hex/number values (not CSS vars), so these mirror the
// Apple tokens in globals.css: primary, primary-focus, primary-on-dark, ink,
// ink-muted-48, plus a light step.
export const CHART_COLORS = [
  "#0066cc",
  "#0071e3",
  "#2997ff",
  "#1d1d1f",
  "#7a7a7a",
  "#aeaeb2",
] as const;

export const CHART_TOOLTIP_STYLE = {
  background: "#ffffff",
  border: "1px solid #e0e0e0",
  borderRadius: 11,
  color: "#1d1d1f",
} as const;
