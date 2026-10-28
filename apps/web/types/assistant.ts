export type AssistantCitation = {
  ref: string; statistic_id:string; geography_id:string; geography:string;
  indicator:string; label:string; estimate:number|null; moe:number|null; unit:string;
  reference_period:string; source:{id:string;title:string;url:string};
  provenance_url:string; workbook_url:string|null; workbook:string|null;
  sheet:string|null; estimate_cell:string|null; moe_cell:string|null;
  universe?:string; method?:string; variables?:string[];
};
export type AssistantProgram = {
  id:string; name:string; administering_agency:string; purpose_benefits:string;
  eligibility_url:string; application_or_referral_url:string; verification_date:string;
  application_availability:string; eligibility_status:string;
  unverified_fields_before_deterministic_matching:string;
};
export type AssistantAnswer = {
  message:string; citations:AssistantCitation[]; district_id:string|null;
  comparisons:{ref:string;left_ref:string;right_ref:string;difference:number;unit:string;method:string}[];
  tools_used:string[]; warnings:string[]; reference_period:string;
  programs?:AssistantProgram[];
  answerability?:string;
  methodology?:string[];
};
export type AssistantMessage = {role:"user"|"assistant";content:string;answer?:AssistantAnswer};
