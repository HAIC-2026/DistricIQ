import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DistrictSelector } from "@/components/maps/DistrictSelector";
import { Dashboard } from "@/components/dashboard/Dashboard";
import { DatasetExplorer } from "@/components/discovery/DatasetExplorer";
import { api } from "@/lib/api";
import report from "./fixtures/discovery-report.json";
vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return { ...actual, api: vi.fn() };
});
vi.mock("next/dynamic", () => ({
  default: () => () => <div aria-label="Map fixture" />,
}));
vi.mock("recharts", () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
  BarChart: () => <div />,
  Bar: () => null,
  XAxis: () => null,
  YAxis: () => null,
  Tooltip: () => null,
  CartesianGrid: () => null,
}));
const mocked = vi.mocked(api);
function mount(children: React.ReactNode) {
  return render(
    <QueryClientProvider
      client={
        new QueryClient({
          defaultOptions: { queries: { retry: false, throwOnError: false } },
        })
      }
    >
      {children}
    </QueryClientProvider>,
  );
}
beforeEach(() => mocked.mockReset());
describe("district workflows", () => {
  it("changes chamber and exposes the documented district count", () => {
    const chamber = vi.fn(),
      number = vi.fn();
    const { rerender } = render(
      <DistrictSelector
        chamber="house"
        number={30}
        onChamber={chamber}
        onNumber={number}
      />,
    );
    expect(screen.getAllByRole("option")).toHaveLength(51);
    fireEvent.click(screen.getByRole("button", { name: /Senate/ }));
    expect(chamber).toHaveBeenCalledWith("senate");
    rerender(
      <DistrictSelector
        chamber="senate"
        number={15}
        onChamber={chamber}
        onNumber={number}
      />,
    );
    expect(screen.getAllByRole("option")).toHaveLength(25);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "7" } });
    expect(number).toHaveBeenCalledWith(7);
  });
  it("updates the profile request when district and chamber change", async () => {
    mocked.mockImplementation(
      async (path) =>
        ({ district: { county: "HONOLULU" }, statistics: [] }) as never,
    );
    mount(<Dashboard />);
    await waitFor(() =>
      expect(mocked).toHaveBeenCalledWith("/v1/districts/house-30/profile"),
    );
    fireEvent.change(
      screen.getByRole("combobox", { name: "Select district" }),
      { target: { value: "12" } },
    );
    await waitFor(() =>
      expect(mocked).toHaveBeenCalledWith("/v1/districts/house-12/profile"),
    );
    expect(screen.getByRole("link", {name:"Ask AI about this district"})).toHaveAttribute("href", "/assistant?district=house-12");
    fireEvent.click(screen.getByRole("button", { name: /Senate/ }));
    await waitFor(() =>
      expect(mocked).toHaveBeenCalledWith("/v1/districts/senate-15/profile"),
    );
    expect(screen.getByRole("link", {name:"Ask AI about this district"})).toHaveAttribute("href", "/assistant?district=senate-15");
  });
  it("shows missing data without fabricated demographic numbers", async () => {
    mocked.mockResolvedValue({
      district: { county: "HONOLULU" },
      statistics: [],
    } as never);
    mount(<Dashboard />);
    await waitFor(() =>
      expect(mocked).toHaveBeenCalledWith("/v1/districts/house-30/profile"),
    );
    expect(screen.getAllByText("Awaiting verified ACS import")).toHaveLength(6);
  });
  it("opens source provenance for a returned statistic", async () => {
    // Synthetic test response only; never shipped as production statistics.
    mocked.mockResolvedValue({
      district: { county: "HONOLULU" },
      statistics: [
        {
          id: "fixture",
          indicator: "population",
          estimate: 12345,
          moe: 321,
          unit: "people",
          reference_period: "2020–2024",
          geographic_level: "house",
          boundary_vintage: 2022,
          variables: ["B01003_001"],
          method: "direct",
          source: {
            id: "test",
            title: "ACS test fixture",
            url: "https://api.census.gov/data/2024/acs/acs5",
          },
          provenance: { test: true },
        },
      ],
    } as never);
    mount(<Dashboard />);
    expect(await screen.findByText("12,345", {selector:".kpi-card strong"})).toBeInTheDocument();
    fireEvent.click(
      screen.getByRole("button", { name: "View source for Total population" }),
    );
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("B01003_001")).toBeInTheDocument();
    fireEvent.click(
      screen.getByRole("button", { name: "Close source details" }),
    );
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
describe("discovery workflows", () => {
  it("renders verified real-source evidence and allows schema inspection", async () => {
    mocked.mockResolvedValue(report as never);
    mount(<DatasetExplorer />);
    expect(
      await screen.findByText("A verified place to start."),
    ).toBeInTheDocument();
    const buttons = screen.getAllByRole("button", { name: "Inspect dataset" });
    fireEvent.click(buttons[0]);
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getAllByText("house_id").length).toBeGreaterThan(0);
    fireEvent.click(
      screen.getByRole("button", { name: "Close dataset details" }),
    );
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
  it("shows the non-destructive ingestion plan", async () => {
    mocked.mockResolvedValue(report as never);
    mount(<DatasetExplorer />);
    const button = await screen.findByRole("button", {
      name: "View safe ingestion plan",
    });
    fireEvent.click(button);
    expect(screen.getByText("Proposed ingestion plan")).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /Execute ingestion/ }),
    ).not.toBeInTheDocument();
  });
});
