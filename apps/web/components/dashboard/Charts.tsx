"use client";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import type { Statistic } from "@/types";
import { formatMoe, formatValue, sourceWorkbookLink } from "@/lib/api";
export function IndicatorChart({
  title,
  subtitle,
  rows,
}: {
  title: string;
  subtitle: string;
  rows: { name: string; stat?: Statistic }[];
}) {
  const vertical = rows.length > 6;
  const available = rows.filter((r) => r.stat?.estimate != null);
  return (
    <section className="panel chart-panel">
      <div className="panel-heading">
        <div>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
        <span className="subtle-tag">ACS 2020–2024</span>
      </div>
      {available.length ? (
        <>
          <div
            className="chart"
            style={{ height: vertical ? rows.length * 28 + 48 : 240 }}
          >
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout={vertical ? "vertical" : "horizontal"}
                data={available.map((r) => ({
                  name: r.name,
                  value: r.stat!.estimate,
                }))}
                margin={{ left: 0, right: 8, top: 10, bottom: 5 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={vertical}
                  horizontal={!vertical}
                  stroke="#e8ece7"
                />
                <XAxis
                  type={vertical ? "number" : "category"}
                  dataKey={vertical ? undefined : "name"}
                  tick={{ fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  type={vertical ? "category" : "number"}
                  dataKey={vertical ? "name" : undefined}
                  tick={{ fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                  width={vertical ? 135 : 45}
                />
                <Tooltip />
                <Bar
                  dataKey="value"
                  fill="#367b60"
                  radius={[4, 4, 0, 0]}
                  maxBarSize={48}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <details className="chart-alternative">
            <summary>View data table and source details</summary>
            <table>
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Estimate</th>
                  <th>90% MOE</th>
                  <th>Source</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.name}>
                    <td>{r.name}</td>
                    <td>{formatValue(r.stat?.estimate, r.stat?.unit)}</td>
                    <td>{formatMoe(r.stat?.moe, r.stat?.unit)}</td>
                    <td>
                      {r.stat && (
                        <a href={sourceWorkbookLink(r.stat.provenance)}>
                          {String(r.stat.provenance.sheet || "")}!
                          {String(r.stat.provenance.estimate_cell || "")} ·{" "}
                          {r.stat.reference_period}
                        </a>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p>
              Direct ACS values or documented sums. Missing categories are
              unavailable.
            </p>
          </details>
        </>
      ) : (
        <div className="chart-empty">
          <div className="empty-bars">
            <i />
            <i />
            <i />
            <i />
            <i />
          </div>
          <strong>Verified data will appear here</strong>
          <p>
            Charts populate after the official ACS import.
            <br />
            No estimates are substituted.
          </p>
        </div>
      )}
    </section>
  );
}
