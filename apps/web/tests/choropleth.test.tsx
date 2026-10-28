import { describe, it, expect } from "vitest";
import { choroplethBreaks, metricUnit } from "@/lib/choropleth";
describe("map legend matches renderer", () => {
  it("covers actual values using four identical color bins", () => {
    const bins = choroplethBreaks([9.8, 10, 14, 18], "percent");
    expect(bins).toHaveLength(4);
    expect(bins[0].min).toBe(9.8);
    expect(bins[3].max).toBe(18);
    expect(bins.every((b) => b.label.includes("%"))).toBe(true);
  });
  it("handles constant values and missing values", () => {
    expect(choroplethBreaks([0, 0], "people")).toHaveLength(1);
    expect(choroplethBreaks([NaN], "people")).toEqual([]);
    expect(metricUnit("median_household_income")).toBe("USD");
  });
});
