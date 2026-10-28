"use client";
import dynamic from "next/dynamic";
import Link from "next/link";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowUpRight,
  Users,
  Wallet,
  HeartHandshake,
  Clock,
  House,
  PersonStanding,
  ShieldCheck,
  Info,
  MapPin,
  ArrowRight,
  MessageCircle,
} from "lucide-react";
import { api } from "@/lib/api";
import type { Chamber, Profile, Statistic } from "@/types";
import { DistrictSelector } from "@/components/maps/DistrictSelector";
import { districtId } from "@/components/maps/DistrictLayer";
import { DemographicCard } from "./DemographicCard";
import { IndicatorChart } from "./Charts";
import { IndicatorTable } from "./IndicatorTable";
import { SourceDetails } from "./SourceDetails";
const Map = dynamic(() => import("@/components/maps/ArcGISMap"), {
  ssr: false,
  loading: () => (
    <div className="map-placeholder">Preparing geographic workspace…</div>
  ),
});
const cards = [
  { code: "population", title: "Total population", Icon: Users },
  {
    code: "median_household_income",
    title: "Median household income",
    Icon: Wallet,
  },
  { code: "poverty_rate", title: "Poverty rate", Icon: HeartHandshake },
  { code: "median_age", title: "Median age", Icon: Clock },
  {
    code: "older_adult_share",
    title: "Residents aged 65+",
    Icon: PersonStanding,
  },
  { code: "median_gross_rent", title: "Median gross rent", Icon: House },
];
export function Dashboard() {
  const [chamber, setChamber] = useState<Chamber>("house"),
    [number, setNumber] = useState(30),
    [metric, setMetric] = useState("boundaries"),
    [source, setSource] = useState<Statistic | null>(null);
  const id = districtId(chamber, number);
  const profile = useQuery({
    queryKey: ["profile", id],
    queryFn: () => api<Profile>(`/v1/districts/${id}/profile`),
  });
  const choropleth = useQuery({
    queryKey: ["choropleth", metric, chamber],
    queryFn: () =>
      api<{ values: Record<string, number> }>(
        `/v1/geography/choropleth?indicator=${metric}&chamber=${chamber}`,
      ),
    enabled: metric !== "boundaries",
  });
  const stat = (code: string) =>
    profile.data?.statistics.find((s) => s.indicator === code);
  function changeChamber(c: Chamber) {
    setChamber(c);
    setNumber(c === "house" ? 30 : 15);
  }
  return (
    <>
      <div className="page-title">
        <div>
          <div className="eyebrow">THE PEOPLE BEHIND THE PLACES</div>
          <h1>Know your district.</h1>
          <p>
            Explore Hawaiʻi’s legislative districts through trusted public data.
          </p>
        </div>
        <Link className="button button-outline" href="/data-explorer">
          Discover datasets <ArrowUpRight size={16} />
        </Link>
      </div>
      <div className="overview-toolbar">
        <DistrictSelector
          chamber={chamber}
          number={number}
          onChamber={changeChamber}
          onNumber={setNumber}
        />
        <span className="verified-label">
          <ShieldCheck size={15} />
          Official 2022 boundaries
        </span>
      </div>
      <div className="map-profile-grid">
        <section className="panel map-panel">
          <div className="panel-heading">
            <div className="inline-heading">
              <MapPin size={17} />
              <h2>District map</h2>
            </div>
            <label className="map-metric-label">
              <span>Color by</span>
              <select
                aria-label="Map indicator"
                value={metric}
                onChange={(e) => setMetric(e.target.value)}
              >
                <option value="boundaries">District boundaries</option>
                <option value="population">Population</option>
                <option value="median_household_income">Median income</option>
                <option value="poverty_rate">Poverty rate</option>
              </select>
            </label>
          </div>
          <Map
            chamber={chamber}
            number={number}
            onSelect={setNumber}
            values={choropleth.data?.values}
            metric={metric}
          />
          {choropleth.isError && (
            <p className="inline-error" role="status">
              Choropleth unavailable until compatible statistics are imported.
            </p>
          )}
        </section>
        <aside className="panel district-profile">
          <div className="profile-kicker">
            <span className="small-square" /> SELECTED DISTRICT
          </div>
          <div className="district-number">
            {String(number).padStart(2, "0")}
            <span>{chamber === "house" ? "HOUSE" : "SENATE"}</span>
          </div>
          <h2>
            {chamber === "house" ? "House" : "Senate"} District {number}
          </h2>
          <p className="district-location">
            <MapPin size={14} />
            {profile.data?.district.county
              ?.replace("HAWAII", "Hawaiʻi")
              .replace("HONOLULU", "Honolulu")
              .replace("OAHU", "Oʻahu · Honolulu County")
              .replace("KAUAI", "Kauaʻi")
              .replace("MAUI", "Maui") || "Hawaiʻi State Legislature"}
          </p>
          <div className="profile-divider" />
          <dl className="profile-facts">
            <dt>Boundary plan</dt>
            <dd>2022 reapportionment</dd>
            <dt>Chamber districts</dt>
            <dd>{chamber === "house" ? 51 : 25}</dd>
            <dt>Statistical period</dt>
            <dd>2020–2024 ACS five-year</dd>
            <dt>Profile status</dt>
            <dd className="status-text">
              {profile.isPending
                ? "Checking availability…"
                : profile.data?.statistics.length
                  ? "Source-backed data"
                  : "Awaiting verified import"}
            </dd>
          </dl>
          <div className="profile-note">
            <Info size={16} />
            <p>
              Every figure includes its source, reference period and available
              margin of error.
            </p>
          </div>
          <Link href="/methodology" className="text-link">
            How the data works <ArrowRight size={14} />
          </Link>
        </aside>
      </div>
      <div className="section-label">
        <h2>District at a glance</h2>
        <span>
          {chamber === "house" ? "House" : "Senate"} District {number} <i /> ACS
          five-year estimates
        </span>
      </div>
      {profile.isError && (
        <div className="notice" role="status">
          <Info size={17} />
          <span>
            <strong>Demographic data is not yet available.</strong>{" "}
            {profile.error.message} The map and dataset discovery remain
            available.
          </span>
        </div>
      )}
      <div className="kpi-grid">
        {cards.map((c) => (
          <DemographicCard
            key={c.code}
            title={c.title}
            Icon={c.Icon}
            statistic={stat(c.code)}
            onSource={setSource}
          />
        ))}
      </div>
      <Link className="button button-primary dashboard-ask-ai" href={`/assistant?district=${id}`}>
        <MessageCircle size={16} /> Ask AI about this district
      </Link>
      <Link
        className="text-link"
        href={`/comparisons?chamber=${chamber}&district=${number}`}
      >
        Compare this district with county and statewide profiles{" "}
        <ArrowRight size={14} />
      </Link>
      <div className="chart-grid">
        <IndicatorChart
          title="Population by age"
          subtitle="Understanding the generations in your district"
          rows={
            profile.data?.statistics.some(
              (s) => s.display_group === "age_distribution",
            )
              ? profile.data.statistics
                  .filter((s) => s.display_group === "age_distribution")
                  .sort(
                    (a, b) => (a.display_order ?? 0) - (b.display_order ?? 0),
                  )
                  .map((s) => ({ name: s.label || s.indicator, stat: s }))
              : [
                  { name: "Under 18", stat: stat("age_under_18") },
                  { name: "18–34", stat: stat("age_18_34") },
                  { name: "35–64", stat: stat("age_35_64") },
                  { name: "65+", stat: stat("age_65_plus") },
                ]
          }
        />
        <IndicatorChart
          title="Housing tenure"
          subtitle="Owner and renter occupied households"
          rows={[
            { name: "Owner occupied", stat: stat("owner_occupied") },
            { name: "Renter occupied", stat: stat("renter_occupied") },
          ]}
        />
        <IndicatorChart
          title="Household income distribution"
          subtitle="Published income brackets, never averaged medians"
          rows={
            profile.data?.statistics.some(
              (s) => s.display_group === "income_distribution",
            )
              ? profile.data.statistics
                  .filter((s) => s.display_group === "income_distribution")
                  .sort(
                    (a, b) => (a.display_order ?? 0) - (b.display_order ?? 0),
                  )
                  .map((s) => ({ name: s.label || s.indicator, stat: s }))
              : Array.from({ length: 16 }, (_, i) => ({
                  name: [
                    "<10k",
                    "10–15k",
                    "15–20k",
                    "20–25k",
                    "25–30k",
                    "30–35k",
                    "35–40k",
                    "40–45k",
                    "45–50k",
                    "50–60k",
                    "60–75k",
                    "75–100k",
                    "100–125k",
                    "125–150k",
                    "150–200k",
                    "200k+",
                  ][i],
                  stat: stat(`income_${String(i + 2).padStart(2, "0")}`),
                }))
          }
        />
        <IndicatorChart
          title="Renter housing cost burden"
          subtitle="Households by reported gross rent as a share of income; universe excludes cases not computed"
          rows={[
            { name: "30–34.9%", stat: stat("rent_burden_30_34") },
            { name: "35% or more", stat: stat("rent_burden_35_plus") },
          ]}
        />
        <section className="panel discovery-callout">
          <span className="callout-icon">
            <ShieldCheck size={24} />
          </span>
          <div className="eyebrow">FROM SOURCE TO INSIGHT</div>
          <h2>
            Good decisions start
            <br />
            with trustworthy data.
          </h2>
          <p>
            Explore official GIS datasets, inspect their schemas, and see
            exactly why a source is recommended.
          </p>
          <Link href="/data-explorer" className="button button-primary">
            Open Data Explorer <ArrowUpRight size={16} />
          </Link>
        </section>
      </div>
      <IndicatorTable
        statistics={profile.data?.statistics || []}
        onSource={setSource}
      />
      <SourceDetails statistic={source} onClose={() => setSource(null)} />
    </>
  );
}
