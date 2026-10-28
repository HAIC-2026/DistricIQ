"use client";
import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { GitCompareArrows, Info } from "lucide-react";
import { DistrictSelector } from "@/components/maps/DistrictSelector";
import { districtId } from "@/components/maps/DistrictLayer";
import { IndicatorChart } from "@/components/dashboard/Charts";
import { api, formatMoe, formatValue, officialLink } from "@/lib/api";
import type { Chamber, Statistic } from "@/types";
type Comparison = {
  district_statistics: Statistic[];
  benchmarks: { name: string; statistics: Statistic[] }[];
  caution: string;
  comparison_rule?: string;
  supplemental_benchmarks?: { name: string; statistics: Statistic[] }[];
};
export default function Page() {
  const [chamber, setChamber] = useState<Chamber>("house"),
    [number, setNumber] = useState(30),
    [benchmark, setBenchmark] = useState("state"),
    [metric, setMetric] = useState("poverty_rate");
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const c = params.get("chamber"),
      n = Number(params.get("district"));
    if (
      (c === "house" || c === "senate") &&
      Number.isInteger(n) &&
      n >= 1 &&
      n <= (c === "house" ? 51 : 25)
    ) {
      setChamber(c);
      setNumber(n);
    }
  }, []);
  const id = districtId(chamber, number);
  const data = useQuery({
    queryKey: ["comparison", id, benchmark],
    queryFn: () => api<Comparison>(`/v1/districts/${id}/compare/${benchmark}`),
  });
  const rows = [
    {
      name: `District ${number}`,
      stat: data.data?.district_statistics.find((s) => s.indicator === metric),
    },
    ...(data.data?.benchmarks.map((b) => ({
      name: b.name,
      stat: b.statistics.find((s) => s.indicator === metric),
    })) || []),
  ];
  const dbedt = [
    ...(data.data?.benchmarks || []),
    ...(data.data?.supplemental_benchmarks || []),
  ]
    .map((b) => ({
      name: b.name,
      stat: b.statistics.find(
        (s) => s.indicator === "dbedt_resident_population",
      ),
    }))
    .filter((b) => b.stat);
  return (
    <>
      <div className="page-title">
        <div>
          <div className="eyebrow">PUT THE NUMBERS IN CONTEXT</div>
          <h1>Compare with perspective.</h1>
          <p>
            See district estimates alongside county and statewide benchmarks.
          </p>
        </div>
        <GitCompareArrows size={28} />
      </div>
      <section className="panel comparison-controls">
        <DistrictSelector
          chamber={chamber}
          number={number}
          onChamber={(c) => {
            setChamber(c);
            setNumber(c === "house" ? 30 : 15);
          }}
          onNumber={setNumber}
        />
        <label>
          Benchmark
          <select
            value={benchmark}
            onChange={(e) => setBenchmark(e.target.value)}
          >
            <option value="state">Hawaiʻi statewide</option>
            <option value="county">Relevant counties</option>
          </select>
        </label>
        <label>
          Indicator
          <select value={metric} onChange={(e) => setMetric(e.target.value)}>
            <option value="poverty_rate">Poverty rate</option>
            <option value="median_household_income">
              Median household income
            </option>
            <option value="median_age">Median age</option>
            <option value="population">Population</option>
          </select>
        </label>
      </section>
      {data.isError && (
        <div className="notice">
          <Info size={18} />
          {data.error.message}
        </div>
      )}
      <IndicatorChart
        title={metric.replaceAll("_", " ")}
        subtitle="Same ACS reference period · original geography retained"
        rows={rows}
      />
      <div className="notice">
        <Info size={18} />
        {data.data?.comparison_rule && (
          <span>
            {data.data.comparison_rule}
            <br />
          </span>
        )}
        {data.data?.caution ||
          "County estimates are contextual benchmarks. They are never substituted for district estimates. Differences are descriptive; no significance test is implied."}
      </div>
      <section className="panel comparison-table">
        <h2>Estimates and uncertainty</h2>
        <table>
          <thead>
            <tr>
              <th>Geography</th>
              <th>Estimate</th>
              <th>90% margin of error</th>
              <th>Period</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.name}>
                <td>{r.name}</td>
                <td>{formatValue(r.stat?.estimate, r.stat?.unit)}</td>
                <td>{formatMoe(r.stat?.moe, r.stat?.unit)}</td>
                <td>{r.stat?.reference_period || "Unavailable"}</td>
                <td>{r.stat?.source.title || "Awaiting official import"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      <section className="panel comparison-table">
        <h2>DBEDT annual population context</h2>
        <p style={{ fontSize: 12, marginBottom: 16 }}>
          July 1, 2024 annual estimates, retained separately from ACS 2020–2024
          survey estimates. No district value is inferred.
        </p>
        {dbedt.length ? (
          <table>
            <thead>
              <tr>
                <th>Published geography</th>
                <th>Population</th>
                <th>Source & reference date</th>
              </tr>
            </thead>
            <tbody>
              {dbedt.map((b) => (
                <tr key={b.name}>
                  <td>{b.name}</td>
                  <td>{formatValue(b.stat?.estimate, "people")}</td>
                  <td>
                    <a
                      href={officialLink(b.stat?.source.url)}
                      target="_blank"
                      rel="noreferrer"
                    >
                      DBEDT table 1.06 ↗
                    </a>
                    <br />
                    {b.stat?.reference_period}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>
            Verified DBEDT context appears after the approved table import.
            Survey margins of error are not published for this annual estimate
            table.
          </p>
        )}
      </section>
    </>
  );
}
