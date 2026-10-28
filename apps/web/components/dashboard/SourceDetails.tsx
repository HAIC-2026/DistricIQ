import { Modal } from "@/components/ui/modal";
import type { Statistic } from "@/types";
import {
  formatMoe,
  formatValue,
  officialLink,
  sourceWorkbookLink,
} from "@/lib/api";
export function SourceDetails({
  statistic,
  onClose,
}: {
  statistic: Statistic | null;
  onClose: () => void;
}) {
  if (!statistic) return null;
  const s = statistic;
  return (
    <Modal className="source-dialog" labelId="source-title" onClose={onClose}>
      <div className="panel-heading">
        <h2 id="source-title">Statistical provenance</h2>
        <button
          className="button button-ghost"
          onClick={onClose}
          aria-label="Close source details"
        >
          Close ×
        </button>
      </div>
      <h3>{s.label || s.indicator.replaceAll("_", " ")}</h3>
      <dl>
        <dt>Estimate</dt>
        <dd>{formatValue(s.estimate, s.unit)}</dd>
        <dt>90% margin of error</dt>
        <dd>{formatMoe(s.moe, s.unit)}</dd>
        <dt>Reference period</dt>
        <dd>{s.reference_period}</dd>
        <dt>Geography</dt>
        <dd>{s.geographic_level}</dd>
        <dt>Boundary plan</dt>
        <dd>{s.boundary_vintage ?? "Not applicable"}</dd>
        <dt>Method</dt>
        <dd>{s.method}</dd>
        <dt>Workbook</dt>
        <dd>{String(s.provenance.workbook || "Not applicable")}</dd>
        <dt>Worksheet / estimate cell</dt>
        <dd>
          {String(s.provenance.sheet || "")}{" "}
          {String(s.provenance.estimate_cell || "")}
        </dd>
        <dt>Original reported value / MOE</dt>
        <dd>
          {String(s.provenance.raw_estimate ?? "Unavailable")} /{" "}
          {String(s.provenance.raw_moe ?? "Unavailable")}
        </dd>
        <dt>Original variables / cells</dt>
        <dd>{s.variables.join(", ")}</dd>
        <dt>Source</dt>
        <dd>
          <a href={officialLink(s.source.url)} target="_blank" rel="noreferrer">
            {s.source.title} ↗
          </a>
        </dd>
      </dl>
      {sourceWorkbookLink(s.provenance) && (
        <a className="text-link" href={sourceWorkbookLink(s.provenance)}>
          Download original source workbook ↗
        </a>
      )}
      <details>
        <summary>Full provenance record</summary>
        <pre>{JSON.stringify(s.provenance, null, 2)}</pre>
      </details>
    </Modal>
  );
}
