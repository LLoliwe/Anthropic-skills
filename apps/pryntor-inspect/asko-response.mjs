export function respond(question,data){
 const text=String(question||'').trim().toLowerCase();
 if(!text)return "Ask about your project, imports, review suggestions or next steps.";
 if(/\b(start|begin|help|hello|hi|hey|sample|upload|what can)\b/.test(text))
  return "Start with Try the sample, or choose your own authorised JavaScript, TypeScript, HTML, CSS or JSON files. Open the architecture map and click a file. No account or upload needed.";
 if(!data)return "I don't have a local report yet. Choose code you own, or try the included two-file sample. Then I can describe its real inventory and notes.";
 const counts=data.counts||{files:0,lines:0,imports:0,notes:0},edges=Array.isArray(data.relationships)?data.relationships:[],files=Array.isArray(data.files)?data.files:[],findings=Array.isArray(data.findings)?data.findings:[];
 if(/\b(security|safe|risk|vulnerab|issue|warning|finding|note|review|error|audit)\b/.test(text)){
  const high=findings.filter(f=>f.severity==='High').length,rev=findings.filter(f=>f.severity==='Review').length,top=findings[0];
  return 'This limited scan flagged '+findings.length+' review notes ('+high+' high-priority patterns, '+rev+' other review patterns). '+(top?'The first is '+top.title+' in '+top.file+' at line '+top.line+'.':'No patterns matched the included ruleset.')+' These are heuristic suggestions, not verified vulnerabilities or a security certificate.';
 }
 if(/\b(import|depend|connect|architecture|graph|relationship|structure|coupling|module)\b/.test(text)){
  const first=edges[0];
  return 'I found '+counts.imports+' listed static imports and '+edges.length+' matched local relationships. '+(first?'For example, '+first.from+' imports '+first.to+'.':'These files have no matched relative-import edges.')+' Select a node in the map to explore possible dependents. This is not a compiler-accurate call graph.';
 }
 if(/\b(file|line|largest|size|count|project|overview|what)\b/.test(text)){
  const largest=[...files].sort((a,b)=>b.lines-a.lines)[0];
  return 'This local scan covers '+counts.files+' files, '+counts.lines+' lines and '+counts.imports+' listed imports. '+(largest?'The largest selected file is '+largest.name+' ('+largest.lines+' lines).':'')+' You can filter files, follow relationships and export JSON without including raw source code.';
 }
 if(/\b(export|download|json|report|share)\b/.test(text))return "Choose Export JSON in the results. The report includes file metadata, detected relationships and review-note locations—but not your source text. Review the report before sharing.";
 if(/\b(ai|model|chatgpt|llm|engine|reverse)\b/.test(text))return "I'm a small on-device, rule-based guide. Asko uses static source heuristics, not a connected language model, the full REA engine or a formal security audit.";
 return 'I can help with this local report: '+counts.files+' files, '+edges.length+' matched import edges and '+counts.notes+' review notes. Ask what to review or how files connect.';
}
