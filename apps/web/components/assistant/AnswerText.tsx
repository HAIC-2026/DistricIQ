import { Fragment, type ReactNode } from "react";
import type { AssistantAnswer } from "@/types/assistant";

type Props = {content:string;answer?:AssistantAnswer;sourcePrefix:string};

/** A deliberately small Markdown surface: no HTML, images, scripts or arbitrary links. */
export function AnswerText({content,answer,sourcePrefix}:Props) {
  const citations=new Map(answer?.citations.map(c=>[c.ref,c]) || []);
  const trustedLinks=new Set(answer?.programs?.flatMap(p=>[p.eligibility_url,p.application_or_referral_url]) || []);
  function inline(text:string):ReactNode[] {
    const nodes:ReactNode[]=[];
    const tokens=/\\([\\`*_{}\[\]<>|])|\*\*(.+?)\*\*|\[([^\]]+)\]\((https:\/\/[^\s)]+)\)|\[(s\d+)\]/g;
    let start=0,match:RegExpExecArray|null;
    while((match=tokens.exec(text))) {
      if(match.index>start)nodes.push(text.slice(start,match.index));
      const key=match.index;
      if(match[1])nodes.push(match[1]);
      else if(match[2])nodes.push(<strong key={key}>{inline(match[2])}</strong>);
      else if(match[3]) {
        let url:URL|undefined;
        try {url=new URL(match[4]);} catch { /* Unknown or malformed links remain text. */ }
        let trusted=trustedLinks.has(match[4]);
        try {trusted ||= trustedLinks.has(decodeURI(match[4]));} catch { /* Malformed percent escapes cannot become links. */ }
        nodes.push(trusted && url?.protocol==="https:" && !url.username && !url.password
          ? <a key={key} href={url.href} target="_blank" rel="noreferrer">{match[3]}</a> : match[3]);
      } else if(match[5] && citations.has(match[5])) {
        const ref=match[5],citation=citations.get(ref)!;
        nodes.push(<a key={key} className="assistant-inline-citation" href={`#${sourcePrefix}-${ref}`} aria-label={`Source ${ref}: ${citation.label}`} onClick={event=>{
          const target=document.getElementById(`${sourcePrefix}-${ref}`);
          if(target){event.preventDefault();const details=target.closest("details");if(details)details.open=true;target.scrollIntoView?.({block:"nearest",behavior:"smooth"});target.focus({preventScroll:true});}
        }}>[{ref}]</a>);
      } else nodes.push(match[0]);
      start=tokens.lastIndex;
    }
    if(start<text.length)nodes.push(text.slice(start));
    return nodes;
  }
  const lines=content.split("\n");
  const blocks:ReactNode[]=[];
  const isTable=(line:string)=>line.trim().startsWith("|") && line.trim().endsWith("|");
  const cells=(line:string)=>line.trim().slice(1,-1).split(/(?<!\\)\|/).map(c=>c.trim());
  for(let i=0;i<lines.length;) {
    if(!lines[i].trim()){i++;continue;}
    const key=i;
    if(isTable(lines[i]) && i+1<lines.length && /^\|(?:\s*:?-+:?\s*\|)+$/.test(lines[i+1].trim())) {
      const header=cells(lines[i]);i+=2;const rows:string[][]=[];
      while(i<lines.length && isTable(lines[i]))rows.push(cells(lines[i++]));
      blocks.push(<div className="assistant-table-scroll" key={key} role="region" aria-label="Statistical findings" tabIndex={0}><table><thead><tr>{header.map((c,j)=><th key={j} scope="col">{inline(c)}</th>)}</tr></thead><tbody>{rows.map((row,j)=><tr key={j}>{row.map((c,k)=><td key={k}>{inline(c)}</td>)}</tr>)}</tbody></table></div>);
    } else if(lines[i].startsWith("- ")) {
      const items:string[]=[];while(i<lines.length && lines[i].startsWith("- "))items.push(lines[i++].slice(2));
      blocks.push(<ul key={key}>{items.map((item,j)=><li key={j}>{inline(item)}</li>)}</ul>);
    } else {
      const paragraph:string[]=[];
      while(i<lines.length && lines[i].trim() && !lines[i].startsWith("- ") && !isTable(lines[i]))paragraph.push(lines[i++]);
      // Unrecognized table-like text is literal, never interpreted as HTML.
      if(!paragraph.length)paragraph.push(lines[i++]);
      blocks.push(<p key={key}>{paragraph.map((line,j)=><Fragment key={j}>{j>0 && <br/>}{inline(line)}</Fragment>)}</p>);
    }
  }
  return <div className="assistant-answer-text">{blocks}</div>;
}
