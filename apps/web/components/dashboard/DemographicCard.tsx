import { Info, ArrowUpRight } from "lucide-react";
import type { Statistic } from "@/types";
import { formatMoe, formatValue } from "@/lib/api";
export function DemographicCard({
  title,
  statistic,
  onSource,
  Icon,
}: {
  title: string;
  statistic?: Statistic;
  onSource: (s: Statistic) => void;
  Icon: React.ComponentType<{ size?: number }>;
}) {
  return (
    <article className="kpi-card">
      <div className="kpi-title">
        <span>{title}</span>
        <Icon size={16} />
      </div>
      <strong
        className={statistic?.estimate == null ? "unavailable-value" : ""}
      >
        {statistic ? formatValue(statistic.estimate, statistic.unit) : "—"}
      </strong>
      <div className="kpi-caption">
        {statistic ? (
          <>
            <span>
              {statistic.reference_period} ACS ·{" "}
              {statistic.moe == null
                ? "MOE unavailable"
                : `± ${formatMoe(statistic.moe, statistic.unit)}`}
            </span>
            <button
              aria-label={`View source for ${title}`}
              onClick={() => onSource(statistic)}
            >
              <Info size={14} />
            </button>
          </>
        ) : (
          <span>Awaiting verified ACS import</span>
        )}
      </div>
    </article>
  );
}
