import type { ChoroplethBreak } from "@/lib/choropleth";
export function ChoroplethLegend({
  title,
  breaks = [],
}: {
  title: string;
  breaks?: ChoroplethBreak[];
}) {
  return (
    <div className="map-legend">
      <strong>{title}</strong>
      {breaks.length ? (
        <>
          {breaks.map((b, i) => (
            <span key={i}>
              <i style={{ background: b.color }} />
              {b.label}
            </span>
          ))}
          <span>
            <i style={{ background: "#dce0dc" }} />
            Unavailable
          </span>
        </>
      ) : (
        <span>
          <i />
          District boundaries <i className="selected-key" />
          Selected district
        </span>
      )}
    </div>
  );
}
