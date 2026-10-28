import React from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Assistant } from "@/components/assistant/Assistant";
import { api } from "@/lib/api";
import type { AssistantAnswer } from "@/types/assistant";

let search = "district=house-30";
vi.mock("next/navigation", () => ({useSearchParams:()=>new URLSearchParams(search)}));
vi.mock("@/lib/api", async () => ({...await vi.importActual<typeof import("@/lib/api")>("@/lib/api"),api:vi.fn()}));
const mocked = vi.mocked(api);
// Synthetic frontend response only. Live tests reconcile real responses with PostgreSQL.
const answer:AssistantAnswer = {
  message:"House District 30 — Total population: 123 people; 90% MOE ±7 people. ACS 2020–2024. [s1]",
  district_id:"house-30", comparisons:[],tools_used:["get_district_indicators"],warnings:[],reference_period:"2020–2024",
  citations:[{ref:"s1",statistic_id:"fixture",geography_id:"house-30",geography:"House District 30",indicator:"population",label:"Total population",estimate:123,moe:7,unit:"people",reference_period:"2020–2024",source:{id:"fixture",title:"Test fixture",url:"https://www.census.gov"},provenance_url:"/v1/statistics/fixture/provenance",workbook_url:"/v1/sources/acs-2024-5yr/workbooks/house",workbook:"fixture.xlsx",sheet:"DP05",estimate_cell:"A4",moe_cell:"B4"}],
};
function mount() {return render(<QueryClientProvider client={new QueryClient({defaultOptions:{queries:{retry:false}}})}><Assistant/></QueryClientProvider>);}
async function send(text:string) {
  fireEvent.change(screen.getByLabelText("Your question"),{target:{value:text}});
  fireEvent.click(screen.getByRole("button",{name:"Send message"}));
  await waitFor(()=>expect(screen.getByRole("button",{name:"Send message"})).toBeDisabled());
  await screen.findByLabelText("Assistant response");
}
beforeEach(()=>{
  sessionStorage.clear();search="district=house-30";window.history.replaceState(null,"","/assistant?district=house-30");
  mocked.mockReset();mocked.mockImplementation(async path=>path.endsWith("status") ? {configured:true} as never : answer as never);
});
describe("AI Assistant",()=>{
  it("shows dated official program sources and preserves incomplete eligibility warnings",async()=>{
    mocked.mockImplementation(async path=>path.endsWith("status") ? {configured:true} as never : {...answer,citations:[],programs:[{id:"ssi",name:"Supplemental Security Income",administering_agency:"SSA",purpose_benefits:"Cash support",eligibility_url:"https://www.ssa.gov/ssi/eligibility",application_or_referral_url:"https://www.ssa.gov/ssi",verification_date:"2026-10-26",application_availability:"Application route published",eligibility_status:"rules_incomplete",unverified_fields_before_deterministic_matching:"Resource exclusions need verification"}]} as never);
    mount(); await send("Which programs support older adults?");
    fireEvent.click(screen.getByText("Official program sources (1)"));
    expect(screen.getByText(/Verified 2026-10-26/)).toBeInTheDocument();
    expect(screen.getByText(/Eligibility rules remain incomplete/)).toBeInTheDocument();
    expect(screen.getByRole("link",{name:/Official eligibility documentation/})).toHaveAttribute("href","https://www.ssa.gov/ssi/eligibility");
  });
  it("preserves dashboard district, displays the answer and original citations",async()=>{
    mount();await screen.findByText("What would you like to understand?");
    expect(screen.getByLabelText("Current district")).toHaveValue("house-30");
    await send("What is the population here?");
    const call=mocked.mock.calls.find(([p])=>p.endsWith("chat"));
    expect(JSON.parse(call![1]!.body as string)).toEqual({message:"What is the population here?",district_id:"house-30",history:[]});
    fireEvent.click(screen.getByText("Sources and margins of error (1)"));
    expect(screen.getByText(/fixture.xlsx · DP05 A4/)).toBeInTheDocument();
    expect(screen.getByRole("link",{name:/View original provenance/})).toHaveAttribute("href","http://localhost:8000/v1/statistics/fixture/provenance");
  });
  it("keeps methodology expandable and renders linked claims without raw Markdown",async()=>{
    mocked.mockImplementation(async path=>path.endsWith("status") ? {configured:true} as never : {...answer,message:"The population is **123 people**. [s1]",methodology:["Detailed comparison method remains accessible."]} as never);
    mount();await send("Population?");
    expect(screen.getByText("123 people").tagName).toBe("STRONG");
    const source=screen.getByRole("link",{name:/Source s1:/});
    fireEvent.click(source);
    expect(screen.getByText(/fixture.xlsx · DP05 A4/).closest("details")).toHaveAttribute("open");
    const details=screen.getByText("Methodology and comparison details").closest("details");
    expect(details).not.toHaveAttribute("open");
    fireEvent.click(screen.getByText("Methodology and comparison details"));
    expect(details).toHaveAttribute("open");
  });
  it("sends follow-up context and honors a changed current district",async()=>{
    mount();await send("Population?");
    fireEvent.change(screen.getByLabelText("Current district"),{target:{value:"senate-15"}});
    fireEvent.change(screen.getByLabelText("Your question"),{target:{value:"And poverty here?"}});
    fireEvent.click(screen.getByRole("button",{name:"Send message"}));
    await waitFor(()=>expect(mocked.mock.calls.filter(([p])=>p.endsWith("chat"))).toHaveLength(2));
    const request=JSON.parse(mocked.mock.calls.filter(([p])=>p.endsWith("chat"))[1][1]!.body as string);
    expect(request.district_id).toBe("senate-15");
    expect(request.history.map((m:{role:string})=>m.role)).toEqual(["user","assistant"]);
  });
  it("shows a recoverable error and keeps the draft without corrupting history",async()=>{
    mocked.mockImplementation(async p=>{if(p.endsWith("status"))return {configured:true} as never;throw new Error("AI service unavailable");});
    mount();fireEvent.change(screen.getByLabelText("Your question"),{target:{value:"My question"}});
    fireEvent.click(screen.getByRole("button",{name:"Send message"}));
    expect(await screen.findByRole("alert")).toHaveTextContent("AI service unavailable");
    expect(screen.getByLabelText("Your question")).toHaveValue("My question");
    expect(screen.queryByLabelText("Your message")).not.toBeInTheDocument();
  });
  it("disables paid requests and explains missing server credentials",async()=>{
    mocked.mockResolvedValue({configured:false} as never);mount();
    expect(await screen.findByText(/AI is not configured yet/)).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Your question"),{target:{value:"hello"}});
    expect(screen.getByRole("button",{name:"Send message"})).toBeDisabled();
  });
  it("rejects invalid linked districts and provides an explicit selector",async()=>{
    search="district=house-99";mount();
    expect(await screen.findByRole("alert")).toHaveTextContent("invalid");
    expect(screen.getByLabelText("Current district")).toHaveValue("");
    expect(screen.getAllByRole("option")).toHaveLength(77);
  });
  it("restores session history and clears it on a new conversation",async()=>{
    sessionStorage.setItem("districtiq-assistant-v1",JSON.stringify({district:"senate-15",messages:[{role:"user",content:"Earlier question"},{role:"assistant",content:"Earlier answer"}]}));
    mount();expect(await screen.findByText("Earlier answer")).toBeInTheDocument();
    expect(screen.getByLabelText("Current district")).toHaveValue("house-30");
    fireEvent.click(screen.getByRole("button",{name:/New conversation/}));
    expect(screen.queryByText("Earlier answer")).not.toBeInTheDocument();
    expect(screen.getByText("What would you like to understand?")).toBeInTheDocument();
  });
  it("discards an interrupted incomplete conversation on restore",async()=>{
    sessionStorage.setItem("districtiq-assistant-v1",JSON.stringify({district:"house-30",messages:[{role:"user",content:"Interrupted request"}]}));
    mount();
    expect(await screen.findByText("What would you like to understand?")).toBeInTheDocument();
    expect(screen.queryByText("Interrupted request")).not.toBeInTheDocument();
  });
});
