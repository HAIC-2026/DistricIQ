"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ArrowUpRight, MessageCircle, Send, Plus, ShieldCheck, LoaderCircle } from "lucide-react";
import { api, apiUrl, formatValue, formatMoe, sourceWorkbookLink } from "@/lib/api";
import { AnswerText } from "./AnswerText";
import type { AssistantAnswer, AssistantMessage } from "@/types/assistant";

const DISTRICT = /^(?:house-(?:0[1-9]|[1-4][0-9]|5[01])|senate-(?:0[1-9]|1[0-9]|2[0-5]))$/;
const STORAGE = "districtiq-assistant-v1";
const options = ["house", "senate"].flatMap(c => Array.from({length:c === "house" ? 51 : 25}, (_,i) => `${c}-${String(i+1).padStart(2,"0")}`));
const title = (id:string) => id ? `${id.startsWith("house") ? "House" : "Senate"} District ${Number(id.split("-")[1])}` : "Choose a district";
const suggestions = ["Summarize this district.", "What are the biggest age groups here?", "Compare this district with the state.", "What percentage of adults have a bachelor’s degree or higher?", "Which official programs support older adults with limited income?"];

function safeProgramUrl(value:string) {
  try {const url=new URL(value); return url.protocol === "https:" && !url.username && !url.password ? url.href : undefined;} catch {return undefined;}
}

export function Assistant() {
  const params = useSearchParams();
  const requested = params.get("district");
  const [district, setDistrict] = useState("");
  const [messages, setMessages] = useState<AssistantMessage[]>([]);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const [ready, setReady] = useState(false);
  const transcript = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const inFlight = useRef(false);
  const status = useQuery({queryKey:["assistant-status"],queryFn:()=>api<{configured:boolean}>("/v1/assistant/status"), retry:false, refetchOnWindowFocus:true});

  useEffect(() => {
    // User/assistant text only; no credentials or server-side response identifiers are persisted.
    try {
      const saved = JSON.parse(sessionStorage.getItem(STORAGE) || "null");
      if (saved && Array.isArray(saved.messages) && saved.messages.length <= 40 && saved.messages.length % 2 === 0 && saved.messages.every((m:AssistantMessage,i:number)=>m.role === (i % 2 === 0 ? "user" : "assistant") && typeof m.content === "string" && m.content.length <= 16000)) {
        setMessages(saved.messages);
        if (DISTRICT.test(saved.district)) setDistrict(saved.district);
      }
    } catch { /* A malformed or blocked session store starts a new conversation. */ }
    setReady(true);
  }, []);
  useEffect(() => {
    if (requested && DISTRICT.test(requested)) {setDistrict(requested);setError("");}
    else if (requested) {setDistrict("");setError("That district identifier is invalid. Choose a House or Senate district below.");}
  }, [requested]);
  useEffect(() => {
    if (ready && !pending) try {sessionStorage.setItem(STORAGE, JSON.stringify({district,messages:messages.slice(-40)}));} catch { /* Chat still works if session storage is blocked. */ }
  }, [district,messages,ready,pending]);
  useEffect(() => {
    if (messages.length || pending) transcript.current?.scrollTo?.({top:transcript.current.scrollHeight,behavior:"smooth"});
  }, [messages,pending]);

  function changeDistrict(id:string) {
    setDistrict(id);setError("");
    const url = new URL(window.location.href);
    if (id) url.searchParams.set("district",id); else url.searchParams.delete("district");
    window.history.replaceState(null,"",url.pathname+url.search);
  }
  async function send(text:string) {
    const question=text.trim();
    if (!question || question.length>2000 || inFlight.current) return;
    inFlight.current=true; setPending(true);setError("");setInput("");
    const prior=messages;
    setMessages([...prior,{role:"user",content:question}]);
    try {
      const history=prior.slice(-8).map(m=>({role:m.role,content:m.content.slice(0,1200)}));
      const answer=await api<AssistantAnswer>("/v1/assistant/chat",{method:"POST",body:JSON.stringify({message:question,district_id:district || null,history})});
      setMessages([...prior,{role:"user",content:question},{role:"assistant",content:answer.message,answer}]);
      if (answer.district_id && DISTRICT.test(answer.district_id)) changeDistrict(answer.district_id);
    } catch (e) {
      setMessages(prior); setInput(question);
      setError(e instanceof Error ? e.message : "Could not send your question. Please retry.");
    } finally {inFlight.current=false;setPending(false);inputRef.current?.focus();}
  }
  function reset() {setMessages([]);setInput("");setError("");inputRef.current?.focus();}

  return <>
    <div className="page-title assistant-title">
      <div><div className="eyebrow">ASK A QUESTION. KNOW YOUR DISTRICT.</div><h1>Your district, explained.</h1><p>Explore the people behind the numbers with the DistrictIQ AI Assistant.</p></div>
      <button className="button button-outline" onClick={reset} disabled={pending}><Plus size={16}/> New conversation</button>
    </div>
    <div className="assistant-layout">
      <section className="panel assistant-chat" aria-label="DistrictIQ AI Assistant">
        <div className="assistant-context"><div className="assistant-avatar"><MessageCircle size={21}/></div><div><h2>AI Assistant</h2><p>Official ACS · 2020–2024</p></div><span className="assistant-source-badge"><ShieldCheck size={14}/> Source grounded</span></div>
        <div className="assistant-district"><label htmlFor="assistant-district">Current district</label><select id="assistant-district" value={district} onChange={e=>changeDistrict(e.target.value)} disabled={pending}><option value="">Choose a district</option>{options.map(id=><option value={id} key={id}>{title(id)}</option>)}</select></div>
        <div ref={transcript} className="assistant-transcript" role="log" aria-label="Conversation" aria-live="polite" aria-relevant="additions">
          {messages.length === 0 && <div className="assistant-welcome"><span className="assistant-welcome-mark"><MessageCircle size={30}/></span><h2>What would you like to understand?</h2><p>Ask about population, education, disability, income, housing or public programs. Compare districts, and trace every estimate to its original source.</p><div className="assistant-suggestions">{suggestions.map(q=><button key={q} onClick={()=>send(q)} disabled={pending || status.data?.configured===false}>{q}<ArrowUpRight size={15}/></button>)}</div></div>}
          {messages.map((m,i)=><article key={i} className={`assistant-message assistant-message-${m.role}`} aria-label={m.role === "user" ? "Your message" : "Assistant response"}><div className="assistant-message-byline">{m.role === "user" ? "YOU" : "DISTRICTIQ ASSISTANT"}</div><AnswerText content={m.content} answer={m.answer} sourcePrefix={`message-${i}-source`}/>{m.answer && m.answer.citations.length>0 && <details className="assistant-citations"><summary>Sources and margins of error ({m.answer.citations.length})</summary>{m.answer.citations.map(c=><div className="assistant-citation" id={`message-${i}-source-${c.ref}`} tabIndex={-1} key={c.ref}><strong>[{c.ref}] {c.geography} · {c.label}</strong><span>{formatValue(c.estimate,c.unit)} · 90% MOE: {formatMoe(c.moe,c.unit)} · ACS {c.reference_period}</span>{c.universe && <span>Population measured: {c.universe}</span>}{c.method && <span>Method: {c.method}</span>}<span>{c.workbook ? `${c.workbook} · ${c.sheet} ${c.estimate_cell || "measure unavailable"}` : c.variables?.join(", ") || "Calculated measure; see source inputs"}{c.moe_cell && ` · MOE ${c.moe_cell}`}</span><a href={apiUrl(c.provenance_url)} target="_blank" rel="noreferrer">View original provenance ↗</a>{sourceWorkbookLink({workbook_url:c.workbook_url}) && <a href={sourceWorkbookLink({workbook_url:c.workbook_url})} target="_blank" rel="noreferrer">Download original workbook ↗</a>}</div>)}</details>}{m.answer?.programs && m.answer.programs.length>0 && <details className="assistant-citations"><summary>Official program sources ({m.answer.programs.length})</summary>{m.answer.programs.map(p=><div className="assistant-citation" key={p.id}><strong>{p.name}</strong><span>{p.administering_agency} · Verified {p.verification_date}</span><span>{p.application_availability}</span><span>Eligibility rules remain incomplete. Confirm current age, income, household, residency and other requirements with the agency.</span><a href={safeProgramUrl(p.eligibility_url)} target="_blank" rel="noreferrer">Official eligibility documentation ↗</a><a href={safeProgramUrl(p.application_or_referral_url)} target="_blank" rel="noreferrer">Official application or referral route ↗</a></div>)}</details>}{m.answer?.methodology && m.answer.methodology.length>0 && <details className="assistant-citations"><summary>Methodology and comparison details</summary><div className="assistant-methodology">{m.answer.methodology.map((text,j)=><p key={j}>{text}</p>)}</div></details>}</article>)}
          {pending && <div className="assistant-pending" role="status"><LoaderCircle size={17}/> Reading verified district data…</div>}
        </div>
        {status.data?.configured===false && <div className="assistant-alert" role="status">AI is not configured yet. Add OPENAI_API_KEY to the server’s root .env and restart FastAPI. You can still use the <Link href="/">district dashboard</Link>.</div>}
        {status.isError && <div className="assistant-alert" role="status">Cannot reach the assistant API. Check that FastAPI is running, then retry your question.</div>}
        {error && <div className="assistant-alert" role="alert">{error}</div>}
        <form className="assistant-composer" onSubmit={e=>{e.preventDefault();void send(input);}}><label className="sr-only" htmlFor="assistant-message">Your question</label><textarea id="assistant-message" ref={inputRef} placeholder={district ? `Ask about ${title(district)}…` : "Ask about a Hawaiʻi House or Senate district…"} value={input} maxLength={2000} rows={2} disabled={pending} onChange={e=>setInput(e.target.value)} onKeyDown={e=>{if(e.key==="Enter" && !e.shiftKey && !e.nativeEvent.isComposing){e.preventDefault();void send(input);}}}/><button className="button button-primary" type="submit" aria-label="Send message" disabled={pending || !input.trim() || status.data?.configured===false}><Send size={17}/><span>Send</span></button></form>
        <div className="assistant-disclosure">AI selects read-only data tools. Statistical values and citations come from the imported ACS records. Enter to send · Shift+Enter for a new line.</div>
      </section>
      <aside className="assistant-help"><section className="panel"><ShieldCheck size={23}/><h2>Answers you can trace.</h2><p>Every reported estimate identifies its geography, reference period and available 90% margin of error.</p><ul><li>76 legislative district profiles</li><li>County and statewide context</li><li>Original workbook citations</li><li>Missing values stay unavailable</li></ul><Link href="/methodology" className="text-link">Sources & methodology <ArrowUpRight size={15}/></Link></section><section className="panel"><h2>Keep the context.</h2><p>“Here” refers to your current district. You can name another district directly, or select one above. Conversation history stays in this browser tab for the session.</p><p>Questions and relevant public data are sent to OpenAI to select tools. The app requests no stored OpenAI response history.</p></section></aside>
    </div>
  </>;
}
