import React from "react";
import { it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { IndicatorTable } from "@/components/dashboard/IndicatorTable";
import type { Statistic } from "@/types";
it("distinguishes reported zero from unavailable values and opens source details", () => {
  const make = (id: string, value: number | null) =>
    ({
      id,
      indicator: id,
      label: id,
      estimate: value,
      moe: null,
      unit: "people",
      reference_period: "2020–2024",
      status: value === null ? "not_published_or_suppressed" : "available",
    }) as Statistic;
  const source = vi.fn();
  render(
    <IndicatorTable
      statistics={[make("zero", 0), make("absent", null)]}
      onSource={source}
    />,
  );
  fireEvent.click(screen.getByText(/All available indicators/));
  expect(screen.getByText("0")).toBeInTheDocument();
  expect(screen.getAllByText("Unavailable").length).toBeGreaterThan(0);
  fireEvent.click(screen.getAllByRole("button", { name: "View source" })[0]);
  expect(source).toHaveBeenCalledWith(expect.objectContaining({ estimate: 0 }));
});
