"use client";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Search,
  ArrowUpRight,
  ShieldCheck,
  Database,
  SlidersHorizontal,
  Info,
  ChevronRight,
  Check,
  LoaderCircle,
  Sparkles,
  FileCheck2,
  Layers,
  X,
} from "lucide-react";
import { api, officialLink } from "@/lib/api";
import type { DiscoveryReport, Evaluation } from "@/types";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
const EXAMPLES = [
  "Find the best official Hawaiʻi State House district boundaries.",
  "Find the latest official State Senate district boundaries.",
  "Find income statistics for House District 30.",
  "Find census tract boundaries for crosswalking.",
];
function Status({ value }: { value: string }) {
  return (
    <span className={`status-badge status-${value}`}>
      {value.replaceAll("_", " ")}
    </span>
  );
}
function Breakdown({ evaluation }: { evaluation: Evaluation }) {
  return (
    <div className="score-breakdown">
      {evaluation.categories.map((c) => (
        <div key={c.criterion}>
          <div className="score-row">
            <span>{c.criterion}</span>
            <b>
              {c.points}
              <small>/{c.maximum}</small>
            </b>
          </div>
          <div className="score-track">
            <i style={{ width: `${(c.points / c.maximum) * 100}%` }} />
          </div>
          <p>{c.evidence}</p>
        </div>
      ))}
    </div>
  );
}
export function DatasetExplorer() {
  const [input, setInput] = useState(EXAMPLES[0]),
    [query, setQuery] = useState(EXAMPLES[0]),
    [ai, setAi] = useState(false),
    [active, setActive] = useState<Evaluation | null>(null),
    [tab, setTab] = useState("all"),
    [compare, setCompare] = useState<string[]>([]),
    [showCompare, setShowCompare] = useState(false),
    [showPlan, setShowPlan] = useState(false);
  const report = useQuery({
    queryKey: ["discovery", query, ai],
    queryFn: () =>
      api<DiscoveryReport>("/v1/discovery/recommend", {
        method: "POST",
        body: JSON.stringify({ query, limit: 8, use_ai: ai }),
      }),
    retry: false,
    staleTime: 300000,
  });
  const results = report.data?.evaluations || [];
  const preferred = results.find((e) => e.status === "recommended");
  const visible = results.filter((e) => tab === "all" || e.status === tab);
  const compared = results.filter((e) =>
    compare.includes(e.dataset.dataset_id),
  );
  function choose(q: string) {
    setInput(q);
    setQuery(q);
    setCompare([]);
    setShowPlan(false);
  }
  return (
    <>
      <div className="page-title">
        <div>
          <div className="eyebrow">DISCOVER. INSPECT. UNDERSTAND.</div>
          <h1>A clearer view of the data.</h1>
          <p>
            Find official geographic sources and follow the evidence behind
            every recommendation.
          </p>
        </div>
        <span className="pill">
          <ShieldCheck size={14} /> Evidence first
        </span>
      </div>
      <section className="discovery-search">
        <div className="search-heading">
          <span className="search-icon">
            <Sparkles size={22} />
          </span>
          <div>
            <h2>Geoportal Data Discovery Agent</h2>
            <p>Ask in plain language. Get sources you can verify.</p>
          </div>
          <span className="subtle-tag">HAWAIʻI STATEWIDE GIS</span>
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (input === query) {
              void report.refetch();
            } else {
              choose(input);
            }
          }}
          className="search-form"
        >
          <Search size={19} />
          <label className="sr-only" htmlFor="discovery-query">
            Dataset discovery request
          </label>
          <input
            id="discovery-query"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            minLength={3}
            maxLength={500}
            required
            placeholder="What geographic data are you looking for?"
          />
          <Button type="submit" disabled={report.isFetching}>
            {report.isFetching ? (
              <LoaderCircle className="spin" size={16} />
            ) : (
              <>
                Find datasets <ArrowUpRight size={16} />
              </>
            )}
          </Button>
        </form>
        <div className="search-examples">
          <span>TRY A SEARCH</span>
          {EXAMPLES.slice(1).map((q, i) => (
            <button key={q} onClick={() => choose(q)}>
              {["Senate boundaries", "District income", "Census tracts"][i]}
              <ArrowUpRight size={12} />
            </button>
          ))}
        </div>
        <label className="ai-option">
          <input
            type="checkbox"
            checked={ai}
            onChange={(e) => setAi(e.target.checked)}
          />{" "}
          Use optional AI to select relevant evidence{" "}
          <span>Deterministic scoring always applies</span>
        </label>
      </section>
      {report.isFetching && (
        <div className="discovery-loading" role="status">
          <LoaderCircle className="spin" size={22} />
          <div>
            <strong>Following the evidence…</strong>
            <p>
              Searching the catalog, inspecting services and checking district
              identifiers.
            </p>
          </div>
        </div>
      )}
      {report.isError && (
        <div role="alert" className="notice error">
          <Info size={20} />
          <div>
            <strong>Discovery is currently unavailable</strong>
            <p>{report.error.message}</p>
            <Button variant="outline" onClick={() => void report.refetch()}>
              Try again
            </Button>
          </div>
        </div>
      )}
      {report.data && !report.isFetching && (
        <>
          <div className="result-meta">
            <span>
              <Database size={15} />
              {results.length} catalog candidates <i />{" "}
              {report.data.mode.replaceAll("_", " ")}
            </span>
            <span>Rubric v1.0.0 · Scores out of 100</span>
          </div>
          {report.data.warning && (
            <div className="notice">
              <Info size={17} />
              {report.data.warning}
            </div>
          )}
          {report.data.statistical_source && (
            <section className="statistical-note">
              <Info size={20} />
              <div>
                <h3>Use different sources for statistics and geometry</h3>
                <p>{report.data.statistical_source.guidance}</p>
                <a
                  href={officialLink(report.data.statistical_source.url)}
                  target="_blank"
                  rel="noreferrer"
                >
                  {report.data.statistical_source.title} ·{" "}
                  {report.data.statistical_source.reference_period}{" "}
                  <ArrowUpRight size={13} />
                </a>
                <small>{report.data.statistical_source.availability}</small>
              </div>
            </section>
          )}
          <div className="explorer-grid">
            <section>
              <div className="results-toolbar">
                <div className="filter-tabs" aria-label="Filter datasets">
                  {[
                    ["all", "All candidates"],
                    ["recommended", "Recommended"],
                    ["rejected", "Rejected"],
                  ].map(([value, label]) => (
                    <button
                      key={value}
                      aria-pressed={tab === value}
                      className={tab === value ? "selected" : ""}
                      onClick={() => setTab(value)}
                    >
                      {label}
                    </button>
                  ))}
                </div>
                <button
                  className="button button-ghost button-small"
                  disabled={compare.length < 2}
                  onClick={() => setShowCompare(true)}
                >
                  <SlidersHorizontal size={15} /> Compare{" "}
                  {compare.length > 0 && `(${compare.length})`}
                </button>
              </div>
              <div className="dataset-list">
                {visible.length ? (
                  visible.map((e) => (
                    <article
                      className={`dataset-card ${e.status === "recommended" ? "recommended-card" : ""}`}
                      key={e.dataset.dataset_id}
                    >
                      <div className="dataset-top">
                        <span className="dataset-icon">
                          <Layers size={21} />
                        </span>
                        <div className="dataset-heading">
                          <Status value={e.status} />
                          <h2>
                            <button onClick={() => setActive(e)}>
                              {e.dataset.title}
                            </button>
                          </h2>
                          <p>{e.dataset.publisher || "Publisher unknown"}</p>
                        </div>
                        <div className="dataset-score">
                          <strong>{e.score}</strong>
                          <span>/100</span>
                        </div>
                      </div>
                      <p className="dataset-description">
                        {e.dataset.description.slice(0, 240)}
                        {e.dataset.description.length > 240 ? "…" : ""}
                      </p>
                      <div className="dataset-facts">
                        <span>
                          {e.dataset.geographic_level || "Geography unknown"}
                        </span>
                        <span>
                          {e.dataset.geographic_vintage
                            ? `${e.dataset.geographic_vintage} boundary plan`
                            : "Vintage unknown"}
                        </span>
                        <span>{e.dataset.format || "Format unknown"}</span>
                        {e.dataset.feature_count != null && (
                          <span>{e.dataset.feature_count} features</span>
                        )}
                      </div>
                      {e.rejections.length > 0 && (
                        <p className="rejection-reason">{e.rejections[0]}</p>
                      )}
                      <div className="dataset-bottom">
                        <label>
                          <input
                            type="checkbox"
                            checked={compare.includes(e.dataset.dataset_id)}
                            onChange={(event) =>
                              setCompare((previous) =>
                                event.target.checked
                                  ? [
                                      ...previous.slice(-2),
                                      e.dataset.dataset_id,
                                    ]
                                  : previous.filter(
                                      (id) => id !== e.dataset.dataset_id,
                                    ),
                              )
                            }
                          />
                          Compare
                        </label>
                        <div>
                          <a
                            href={officialLink(
                              e.dataset.service_url || e.dataset.catalog_url,
                            )}
                            target="_blank"
                            rel="noreferrer"
                          >
                            Official source <ArrowUpRight size={13} />
                          </a>
                          <button onClick={() => setActive(e)}>
                            Inspect dataset <ChevronRight size={14} />
                          </button>
                        </div>
                      </div>
                    </article>
                  ))
                ) : (
                  <div className="panel empty-state">
                    <Database size={28} />
                    <h2>No candidates in this view</h2>
                    <p>
                      Try another filter or a more specific geographic request.
                    </p>
                  </div>
                )}
              </div>
            </section>
            <aside className="recommendation-column">
              <section className="recommendation-panel">
                <div className="recommendation-label">
                  <ShieldCheck size={17} /> SOURCE RECOMMENDATION
                </div>
                <h2>
                  {preferred
                    ? "A verified place to start."
                    : "More evidence is needed."}
                </h2>
                <p>{report.data.explanation}</p>
                {preferred && (
                  <>
                    <div className="recommended-source">
                      <FileCheck2 size={22} />
                      <div>
                        <strong>{preferred.dataset.title}</strong>
                        <span>{preferred.score}/100 · service inspected</span>
                      </div>
                    </div>
                    <ul className="evidence-list">
                      {preferred.positives.slice(0, 4).map((p) => (
                        <li key={p}>
                          <Check size={14} />
                          {p}
                        </li>
                      ))}
                    </ul>
                    <Button
                      variant="outline"
                      onClick={() => setActive(preferred)}
                    >
                      View ranking evidence <ArrowUpRight size={14} />
                    </Button>
                  </>
                )}
                <div className="recommendation-footnote">
                  <Info size={14} />
                  <span>
                    Recommendation is separate from approval. Ingestion requires
                    local developer review.
                  </span>
                </div>
              </section>
              <section className="panel plan-panel">
                <div className="inline-heading">
                  <FileCheck2 size={18} />
                  <h3>From discovery to ingestion</h3>
                </div>
                <p>
                  Review the proposed transformations, destination and
                  validation checks.
                </p>
                <Button
                  variant="ghost"
                  disabled={!report.data.ingestion_plan}
                  onClick={() => setShowPlan(!showPlan)}
                >
                  View safe ingestion plan <ArrowRightIcon />
                </Button>
              </section>
              <div className="agent-status">
                <span className="live-dot" />
                {report.data.ai.message ||
                  "Deterministic discovery · AI assistance optional"}
                {report.data.ai.evidence_highlights?.map((e) => (
                  <p key={e}>{e}</p>
                ))}
              </div>
            </aside>
          </div>
          {showPlan && report.data.ingestion_plan && (
            <section className="panel full-plan">
              <div className="panel-heading">
                <h2>Proposed ingestion plan</h2>
                <Status value="review_required" />
              </div>
              <p>{report.data.ingestion_plan.destination}</p>
              <h3>Transformations</h3>
              <ol>
                {report.data.ingestion_plan.transformations.map((t) => (
                  <li key={t}>{t}</li>
                ))}
              </ol>
              <h3>Validation requirements</h3>
              <ul>
                {report.data.ingestion_plan.validations.map((t) => (
                  <li key={t}>{t}</li>
                ))}
              </ul>
              <div className="notice">
                <Info size={17} />
                {report.data.ingestion_plan.next_step}
              </div>
            </section>
          )}
        </>
      )}
      {active && (
        <Modal
          className="dataset-dialog"
          labelId="dataset-title"
          onClose={() => setActive(null)}
        >
          <div className="dialog-sticky">
            <span className="eyebrow">DATASET EVIDENCE</span>
            <Button
              variant="ghost"
              onClick={() => setActive(null)}
              aria-label="Close dataset details"
            >
              <X size={18} />
            </Button>
          </div>
          <Status value={active.status} />
          <h2 id="dataset-title">{active.dataset.title}</h2>
          <p>{active.dataset.description}</p>
          <a
            className="text-link"
            href={officialLink(
              active.dataset.service_url || active.dataset.catalog_url,
            )}
            target="_blank"
            rel="noreferrer"
          >
            Open official source <ArrowUpRight size={14} />
          </a>
          <dl className="metadata-grid">
            <dt>Catalog retrieved</dt>
            <dd>{new Date(active.dataset.retrieved_at).toLocaleString()}</dd>
            <dt>Metadata modified</dt>
            <dd>{active.dataset.modified_date || "Unknown"}</dd>
            <dt>Boundary vintage</dt>
            <dd>{active.dataset.geographic_vintage || "Unknown"}</dd>
            <dt>Statistical reference year</dt>
            <dd>
              {active.dataset.reference_year || "Unknown / not applicable"}
            </dd>
            <dt>Geometry</dt>
            <dd>
              {active.dataset.inspection?.geometry_type || "Not inspected"}
            </dd>
          </dl>
          <h3>Reproducible suitability score · {active.score}/100</h3>
          <Breakdown evaluation={active} />
          <h3>Limitations & checks</h3>
          <ul>
            {[...active.rejections, ...active.limitations].map((x) => (
              <li key={x}>{x}</li>
            ))}
          </ul>
          <h3>Verified field schema</h3>
          {active.dataset.inspection?.fields ? (
            <table>
              <thead>
                <tr>
                  <th>Field</th>
                  <th>Type</th>
                </tr>
              </thead>
              <tbody>
                {active.dataset.inspection.fields.map((f) => (
                  <tr key={f.name}>
                    <td>{f.name}</td>
                    <td>{f.type}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>
              Field schema unavailable. Catalog metadata alone cannot verify
              attributes.
            </p>
          )}
          <details>
            <summary>Extent and spatial reference</summary>
            <pre>
              {JSON.stringify(
                {
                  extent: active.dataset.inspection?.extent,
                  spatial_reference:
                    active.dataset.inspection?.spatial_reference,
                },
                null,
                2,
              )}
            </pre>
          </details>
          <details>
            <summary>Source license and use conditions</summary>
            <p>{active.dataset.license || "Unknown; review required"}</p>
          </details>
        </Modal>
      )}
      {showCompare && (
        <Modal
          className="dataset-dialog comparison-dialog"
          labelId="compare-title"
          onClose={() => setShowCompare(false)}
        >
          <div className="panel-heading">
            <h2 id="compare-title">Compare recorded evidence</h2>
            <Button
              variant="ghost"
              onClick={() => setShowCompare(false)}
              aria-label="Close comparison"
            >
              <X size={18} />
            </Button>
          </div>
          <div className="comparison-candidates">
            {compared.map((e) => (
              <div key={e.dataset.dataset_id}>
                <h3>{e.dataset.title}</h3>
                <Status value={e.status} />
                <h2>{e.score}/100</h2>
                <Breakdown evaluation={e} />
              </div>
            ))}
          </div>
        </Modal>
      )}
    </>
  );
}
function ArrowRightIcon() {
  return <ChevronRight size={15} />;
}
