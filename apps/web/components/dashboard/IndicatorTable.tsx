import type { Statistic } from "@/types";
import { formatValue, formatMoe } from "@/lib/api";
export function IndicatorTable({
  statistics,
  onSource,
}: {
  statistics: Statistic[];
  onSource: (s: Statistic) => void;
}) {
  return (
    <details className="panel indicator-table">
      <summary>
        All available indicators and sources ({statistics.length})
      </summary>
      <div className="indicator-table-scroll">
        <table>
          <thead>
            <tr>
              <th>Indicator</th>
              <th>Estimate</th>
              <th>90% margin of error</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            {statistics.map((s) => (
              <tr key={s.id}>
                <td>
                  {s.label || s.indicator.replaceAll("_", " ")}
                  {s.estimate === null && (
                    <small className="availability-note">
                      {s.status.replaceAll("_", " ")}
                    </small>
                  )}
                </td>
                <td>{formatValue(s.estimate, s.unit)}</td>
                <td>{formatMoe(s.moe, s.unit)}</td>
                <td>
                  <button className="text-link" onClick={() => onSource(s)}>
                    View source
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p>
        All figures retain their original geography and the 2020–2024 ACS
        reference period. Missing values remain unavailable.
      </p>
    </details>
  );
}
