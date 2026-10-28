import { formatValue } from "./api";
export type ChoroplethBreak = {
  min: number;
  max: number;
  color: string;
  label: string;
};
export function choroplethBreaks(
  values: number[],
  unit: string,
): ChoroplethBreak[] {
  const valid = values.filter(Number.isFinite);
  if (!valid.length) return [];
  const min = Math.min(...valid),
    max = Math.max(...valid);
  const colors = ["#dcece4", "#a6ccb9", "#64a68b", "#23785d"];
  if (min === max)
    return [{ min, max, color: colors[3], label: formatValue(min, unit) }];
  const step = (max - min) / 4;
  return colors.map((color, i) => {
    const lo = min + i * step,
      hi = i === 3 ? max : min + (i + 1) * step;
    return {
      min: lo,
      max: hi,
      color,
      label: `${formatValue(lo, unit)} – ${formatValue(hi, unit)}`,
    };
  });
}
export function metricUnit(metric: string) {
  return metric === "median_household_income"
    ? "USD"
    : metric === "poverty_rate"
      ? "percent"
      : "people";
}
