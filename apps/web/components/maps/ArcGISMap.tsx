"use client";
import { useEffect, useRef, useState } from "react";
import { Expand, Layers, LoaderCircle, MapPin } from "lucide-react";
import type MapView from "@arcgis/core/views/MapView";
import type GeoJSONLayer from "@arcgis/core/layers/GeoJSONLayer";
import { choroplethBreaks, metricUnit } from "@/lib/choropleth";
import { apiUrl } from "@/lib/api";
import type { GeoJSONLayerProperties } from "@arcgis/core/layers/GeoJSONLayer";
import type { SimpleRendererProperties } from "@arcgis/core/renderers/SimpleRenderer";
import type { ClassBreaksRendererProperties } from "@arcgis/core/renderers/ClassBreaksRenderer";
import type { GraphicHit } from "@arcgis/core/views/types";
import type { Chamber } from "@/types";
import { layers } from "./DistrictLayer";
import { ChoroplethLegend } from "./ChoroplethLegend";
type Props = {
  chamber: Chamber;
  number: number;
  onSelect: (v: number) => void;
  values?: Record<string, number>;
  metric: string;
};
export default function ArcGISMap({
  chamber,
  number,
  onSelect,
  values,
  metric,
}: Props) {
  const container = useRef<HTMLDivElement>(null),
    viewRef = useRef<MapView | null>(null),
    layerRef = useRef<GeoJSONLayer | null>(null);
  const callback = useRef(onSelect);
  callback.current = onSelect;
  const [selectionStatus, setSelectionStatus] = useState(
    "Preparing district selection…",
  );
  const [ready, setReady] = useState(false),
    [error, setError] = useState("");
  useEffect(() => {
    let disposed = false;
    let destroy: (() => void) | undefined;
    setReady(false);
    setError("");
    async function init() {
      try {
        const [
          { default: Map },
          { default: View },
          { default: FL },
          { default: Basemap },
          { default: TileLayer },
        ] = await Promise.all([
          import("@arcgis/core/Map"),
          import("@arcgis/core/views/MapView"),
          import("@arcgis/core/layers/GeoJSONLayer"),
          import("@arcgis/core/Basemap"),
          import("@arcgis/core/layers/TileLayer"),
        ]);
        if (disposed || !container.current) return;
        const layer = new FL({
          url: apiUrl(`/v1/geography/districts?chamber=${chamber}`),
          objectIdField: "objectid",
          copyright:
            "Hawaiʻi Statewide GIS Program · official 2022 reapportionment · local PostGIS capture",
          outFields: ["*"],
          popupEnabled: false,
          title: `2022 State ${chamber} districts`,
          renderer: {
            type: "simple",
            symbol: {
              type: "simple-fill",
              color: [61, 113, 96, 0.1],
              outline: { color: [50, 100, 84, 0.8], width: 1 },
            },
          },
        } as GeoJSONLayerProperties);
        const map = new Map({
          basemap: new Basemap({
            baseLayers: [
              new TileLayer({
                url: "https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer",
              }),
            ],
          }),
          layers: [layer],
        });
        const view = new View({
          container: container.current,
          map,
          center: [-157.1, 20.65],
          zoom: 6,
          ui: { components: ["zoom"] },
          constraints: { minZoom: 5 },
          highlights: [
            {
              name: "default",
              color: [16, 76, 58, 1],
              haloOpacity: 0.9,
              fillOpacity: 0.25,
            },
          ],
        });
        viewRef.current = view;
        layerRef.current = layer;
        const click = view.on("click", async (e) => {
          const response = await view.hitTest(e, { include: [layer] });
          const graphic = response.results.find((r) => r.type === "graphic") as
            | GraphicHit
            | undefined;
          const n = Number(
            graphic?.graphic.attributes?.[layers[chamber].field],
          );
          if (n) callback.current(n);
          else
            setSelectionStatus(
              graphic
                ? "The clicked feature has no district identifier."
                : "Choose a district polygon or use the district selector.",
            );
        });
        destroy = () => {
          click.remove();
          view.destroy();
          viewRef.current = null;
          layerRef.current = null;
        };
        await Promise.all([view.when(), layer.load()]);
        if (!disposed) setReady(true);
      } catch (e) {
        if (!disposed)
          setError(e instanceof Error ? e.message : "Map service unavailable");
      }
    }
    void init();
    return () => {
      disposed = true;
      destroy?.();
    };
  }, [chamber]);
  useEffect(() => {
    if (!ready || !viewRef.current || !layerRef.current) return;
    let disposed = false;
    let highlight: { remove: () => void } | undefined;
    const view = viewRef.current,
      layer = layerRef.current;
    async function select() {
      try {
        const q = layer.createQuery();
        q.where = `${layers[chamber].field} = ${number}`;
        q.returnGeometry = true;
        const results = await layer.queryFeatures(q);
        if (disposed) return;
        if (!results.features.length) {
          setSelectionStatus(
            "Selected district was not found in the map layer.",
          );
          return;
        }
        const lv = await view.whenLayerView(layer);
        if (disposed) return;
        highlight = lv.highlight(results.features);
        setSelectionStatus(
          `${chamber === "house" ? "House" : "Senate"} District ${number} highlighted`,
        );
        await view.goTo(
          {
            target:
              results.features[0].geometry?.extent?.expand(1.2) ||
              results.features[0],
          },
          { animate: false },
        );
      } catch (e) {
        if (!disposed)
          setSelectionStatus(
            "Map selection could not complete: " +
              (e instanceof Error ? e.message : "map query unavailable"),
          );
      }
    }
    void select();
    return () => {
      disposed = true;
      highlight?.remove();
    };
  }, [ready, chamber, number]);
  useEffect(() => {
    if (!ready || !layerRef.current) return;
    void (async () => {
      const { default: Renderer } = await import(
        "@arcgis/core/renderers/ClassBreaksRenderer"
      );
      const { default: SimpleRenderer } = await import(
        "@arcgis/core/renderers/SimpleRenderer"
      );
      const layer = layerRef.current;
      if (!layer) return;
      if (!values || !Object.keys(values).length) {
        layer.renderer = new SimpleRenderer({
          symbol: {
            type: "simple-fill",
            color: [61, 113, 96, 0.1],
            outline: { color: [50, 100, 84, 0.8], width: 1 },
          },
        } as SimpleRendererProperties);
        return;
      }
      const entries = Object.entries(values).filter(
        ([key, v]) => key.startsWith(chamber + "-") && Number.isFinite(v),
      );
      const nums = entries.map(([, v]) => v);
      if (!nums.length) return;
      const breaks = choroplethBreaks(nums, metricUnit(metric));
      const expression =
        "When(" +
        entries
          .map(
            ([key, v]) =>
              `$feature.${layers[chamber].field} == ${Number(key.split("-")[1])}, ${v}`,
          )
          .join(", ") +
        ", null)";
      layer.renderer = new Renderer({
        valueExpression: expression,
        valueExpressionTitle: metric,
        defaultSymbol: {
          type: "simple-fill",
          color: [220, 224, 220],
          outline: { color: "#fff", width: 0.5 },
        },
        classBreakInfos: breaks.map((b) => ({
          minValue: b.min,
          maxValue: b.max,
          label: b.label,
          symbol: {
            type: "simple-fill",
            color: b.color,
            outline: { color: "#ffffff", width: 0.7 },
          },
        })),
      } as ClassBreaksRendererProperties);
    })();
  }, [ready, values, chamber, metric]);
  const nums = values
    ? Object.entries(values)
        .filter(([k]) => k.startsWith(chamber + "-"))
        .map(([, v]) => v)
    : [];
  return (
    <div className="map-wrap">
      <div
        ref={container}
        className="map-canvas"
        aria-label={`Interactive map of Hawaiʻi State ${chamber} districts`}
      />
      {!ready && !error && (
        <div className="map-loading">
          <LoaderCircle className="spin" size={23} />
          Loading official ArcGIS boundaries…
        </div>
      )}
      {error && (
        <div className="map-loading map-error">
          <MapPin size={28} />
          <strong>Map could not load</strong>
          <span>
            Use the district selector to explore profiles. The official layer
            may be temporarily unavailable.
          </span>
          <a href={layers[chamber].url} target="_blank" rel="noreferrer">
            Inspect official layer
          </a>
        </div>
      )}
      <div role="status" className="map-selection-status">
        {selectionStatus}
      </div>
      <div className="map-top-label">
        <span className="live-dot" /> OFFICIAL LEGISLATIVE BOUNDARIES
      </div>
      <button
        className="map-reset"
        aria-label="Show all Hawaiʻi districts"
        onClick={() =>
          void viewRef.current?.goTo({ center: [-157.1, 20.65], zoom: 6 })
        }
      >
        <Expand size={17} />
      </button>
      <div className="map-badge">
        <Layers size={14} />
        2022 reapportionment
      </div>
      <ChoroplethLegend
        title={
          nums.length
            ? metric.replaceAll("_", " ")
            : "HAWAIʻI · STATE LEGISLATIVE DISTRICTS"
        }
        breaks={choroplethBreaks(nums, metricUnit(metric))}
      />
    </div>
  );
}
