export type Chamber = "house" | "senate";
export type Statistic = {
  id: string;
  indicator: string;
  label?: string;
  display_group?: string | null;
  display_order?: number;
  estimate: number | null;
  moe: number | null;
  unit: string;
  reference_period: string;
  geographic_level: string;
  boundary_vintage: number | null;
  variables: string[];
  method: string;
  status: string;
  source: { id: string; title: string; url: string };
  provenance: Record<string, unknown>;
};
export type District = {
  id: string;
  chamber: Chamber;
  number: number;
  name: string;
  county: string | null;
  boundary_vintage: number;
  source_id: string;
};
export type Profile = { district: District; statistics: Statistic[] };
export type Category = {
  criterion: string;
  points: number;
  maximum: number;
  evidence: string;
};
export type Dataset = {
  dataset_id: string;
  title: string;
  publisher: string | null;
  description: string;
  service_url: string | null;
  catalog_url: string | null;
  geographic_level: string | null;
  geographic_vintage: number | null;
  reference_year: number | null;
  modified_date: string | null;
  retrieved_at: string;
  format: string | null;
  validation_status: string;
  available_fields: string[];
  feature_count: number | null;
  license: string | null;
  inspection: {
    geometry_type?: string;
    spatial_reference?: Record<string, unknown>;
    extent?: Record<string, unknown>;
    credits?: string;
    retrieved_at?: string;
    fields?: { name: string; type: string; alias: string }[];
  } | null;
};
export type Evaluation = {
  dataset: Dataset;
  score: number;
  status: string;
  categories: Category[];
  positives: string[];
  limitations: string[];
  rejections: string[];
};
export type Plan = {
  source_url: string;
  destination: string;
  transformations: string[];
  validations: string[];
  next_step: string;
  executable: boolean;
};
export type DiscoveryReport = {
  evaluation_id: string;
  query: string;
  mode: string;
  warning: string | null;
  evaluations: Evaluation[];
  recommendation: string | null;
  explanation: string;
  ingestion_plan: Plan | null;
  statistical_source: {
    title: string;
    url: string;
    reference_period: string;
    guidance: string;
    availability: string;
  } | null;
  ai: {
    enabled: boolean;
    status: string;
    evidence_highlights?: string[];
    message?: string;
  };
};
