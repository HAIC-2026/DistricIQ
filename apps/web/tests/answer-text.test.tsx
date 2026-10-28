import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnswerText } from "@/components/assistant/AnswerText";
import type { AssistantAnswer } from "@/types/assistant";

const answer:AssistantAnswer={message:"",district_id:"house-30",comparisons:[],warnings:[],tools_used:[],reference_period:"2020–2024",citations:[{
  ref:"s1",statistic_id:"fixture",geography_id:"house-30",geography:"House District 30",indicator:"population",label:"Total population",estimate:123,moe:7,unit:"people",reference_period:"2020–2024",source:{id:"fixture",title:"ACS",url:"https://census.gov"},provenance_url:"/fixture",workbook_url:null,workbook:null,sheet:null,estimate_cell:null,moe_cell:null,
}]};

describe("Research answer presentation",()=>{
  it("renders paragraphs, emphasized values and readable lists",()=>{
    const {container}=render(<AnswerText sourcePrefix="test" answer={answer} content={"A direct answer with **123 people**. [s1]\n\n**Key findings**\n\n- First finding\n- Second finding"}/>);
    expect(screen.getByText("123 people").tagName).toBe("STRONG");
    expect(screen.getAllByRole("listitem")).toHaveLength(2);
    expect(container.querySelectorAll("p")).toHaveLength(2);
    expect(screen.getByRole("link",{name:"Source s1: Total population"})).toHaveAttribute("href","#test-s1");
  });
  it("renders an accessible comparison table with column headings and source references",()=>{
    render(<AnswerText sourcePrefix="test" answer={answer} content={"| Measure | House District 30 | House District 31 |\n| --- | --- | --- |\n| Population | **123 people** [s1] | 100 people |"}/>);
    expect(screen.getAllByRole("columnheader")).toHaveLength(3);
    expect(within(screen.getByRole("table")).getByText("123 people")).toBeInTheDocument();
    expect(screen.getByRole("region",{name:"Statistical findings"})).toHaveAttribute("tabindex","0");
  });
  it("opens and focuses the correct source panel when an inline reference is clicked",()=>{
    render(<><AnswerText sourcePrefix="test" answer={answer} content="The estimate is **123 people**. [s1]"/><details data-testid="sources"><summary>Sources</summary><div id="test-s1" tabIndex={-1}>Original record</div></details></>);
    fireEvent.click(screen.getByRole("link",{name:/Source s1/}));
    expect(screen.getByTestId("sources")).toHaveAttribute("open");
    expect(screen.getByText("Original record")).toHaveFocus();
  });
  it("keeps HTML, unknown citations and untrusted links inert",()=>{
    const {container}=render(<AnswerText sourcePrefix="test" content={'<img src=x onerror=alert(1)> [s99] [unsafe](https://evil.example/) [script](javascript:alert(1))'}/>);
    expect(container.querySelector("img")).toBeNull();
    expect(screen.queryByRole("link")).not.toBeInTheDocument();
    expect(screen.getByText(/\[s99\]/)).toBeInTheDocument();
  });
  it("allows only links present in retrieved official program records",()=>{
    const program={id:"example",name:"Example program",administering_agency:"Agency",purpose_benefits:"Support",eligibility_url:"https://example.gov/rules",application_or_referral_url:"https://example.gov/apply",verification_date:"2026-10-26",application_availability:"Published",eligibility_status:"rules_incomplete",unverified_fields_before_deterministic_matching:"Incomplete"};
    render(<AnswerText sourcePrefix="test" answer={{...answer,programs:[program]}} content={"**[Example program](https://example.gov/rules)** [untrusted](https://other.example/) [malformed](https://example.gov/%zz)"}/>);
    expect(screen.getAllByRole("link")).toHaveLength(1);
    expect(screen.getByRole("link",{name:"Example program"})).toHaveAttribute("href",program.eligibility_url);
  });
  it("preserves literal escaped label punctuation inside table cells",()=>{
    render(<AnswerText sourcePrefix="test" content={"| Measure | Estimate |\n| --- | --- |\n| A \\| B \\[s99\\] | **10** |"}/>);
    expect(screen.getAllByRole("cell")).toHaveLength(2);
    expect(screen.getByText("A | B [s99]")).toBeInTheDocument();
  });
});
