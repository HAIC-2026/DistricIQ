import {
  ShieldCheck,
  Database,
  Layers,
  ArrowUpRight,
  Info,
} from "lucide-react";
export default function Page() {
  return (
    <>
      <div className="page-title">
        <div>
          <div className="eyebrow">TRANSPARENCY AT EVERY STEP</div>
          <h1>Evidence you can follow.</h1>
          <p>
            Where the data comes from, what it means, and where its limits
            begin.
          </p>
        </div>
        <ShieldCheck size={28} />
      </div>
      <div className="methodology-grid">
        <section className="panel prose">
          <Layers size={24} />
          <h2>Official geographic boundaries</h2>
          <p>
            The Hawaiʻi Statewide GIS Program publishes the 2022 reapportionment
            boundaries. DistrictIQ inspects the underlying ArcGIS layers,
            verifies all 51 House and 25 Senate identifiers, and requires
            approval before importing geometry into PostGIS.
          </p>
          <a
            href="https://geodata.hawaii.gov/arcgis/rest/services/AdminBnd/MapServer/33"
            target="_blank"
            rel="noreferrer"
          >
            House district layer <ArrowUpRight size={13} />
          </a>
          <a
            href="https://geodata.hawaii.gov/arcgis/rest/services/AdminBnd/MapServer/34"
            target="_blank"
            rel="noreferrer"
          >
            Senate district layer <ArrowUpRight size={13} />
          </a>
        </section>
        <section className="panel prose">
          <Database size={24} />
          <h2>ACS five-year estimates</h2>
          <p>
            The 2024 ACS five-year product covers 2020–2024. It combines survey
            observations across that period. Estimates describe the reference
            period and carry sampling uncertainty; they are not a single-year
            population count.
          </p>
          <p>
            DistrictIQ retains original variable identifiers, 90% margins of
            error, source links, suppressed values and ingestion records. Direct
            legislative-district estimates are preferred.
          </p>
          <a
            href="https://api.census.gov/data/2024/acs/acs5.html"
            target="_blank"
            rel="noreferrer"
          >
            Official ACS dataset <ArrowUpRight size={13} />
          </a>
        </section>
        <section className="panel prose">
          <ShieldCheck size={24} />
          <h2>Reproducible source evaluation</h2>
          <p>
            Code assigns the score from recorded evidence. The seven categories
            total 100 points: authority 25, geography 20, vintage 15, schema 15,
            completeness 10, access 10 and methodology 5.
          </p>
          <p>
            A score cannot override a hard rejection. Wrong chamber,
            incompatible vintage, missing required fields and incomplete
            district coverage prevent recommendation. Missing evidence produces
            a review state.
          </p>
          <p>
            Optional AI selects relevant recorded evidence. It cannot create
            statistics, change scores or approve ingestion.
          </p>
        </section>
        <section className="panel prose">
          <Info size={24} />
          <h2>Crosswalks & uncertainty</h2>
          <p>
            Crosswalking is reserved for additive counts when direct district
            values are unavailable. Population weights require verified block
            assignments. Area weights require an explicit justification and
            equal-area projection.
          </p>
          <p>
            Source weights must sum to one and allocated counts must conserve
            the original total. Medians, percentages and rates are never
            directly averaged. Rates can be recomputed from compatible counts.
          </p>
          <p>
            Allocation adds model uncertainty beyond a published survey margin
            of error. Derived results must be labelled estimated.
          </p>
        </section>
      </div>
      <section className="panel prose">
        <h2>Boundary compatibility and comparisons</h2>
        <p>
          The Census Bureau documents 2024 legislative plan changes. Hawaiʻi is
          among the states with no plan changes from the 2022 cycle. District
          identifiers and counts are still validated during every import.
        </p>
        <a
          href="https://www.census.gov/programs-surveys/acs/technical-documentation/table-and-geography-changes/2024/geography-changes.html"
          target="_blank"
          rel="noreferrer"
        >
          Census 2024 geography changes <ArrowUpRight size={13} />
        </a>
        <p>
          County and state values remain at their published geographic levels.
          Multiple relevant counties are presented separately. Comparisons
          between overlapping geographies are descriptive and do not establish
          statistical significance or individual resident characteristics.
        </p>
      </section>
      <div className="notice">
        <Info size={18} />
        This research preview uses public, aggregated data. It provides no
        individual eligibility determination or inference about specific
        residents.
      </div>
    </>
  );
}
