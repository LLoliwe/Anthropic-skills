// Deterministic, privacy-preserving change-impact analysis from the existing local import graph.
// Edges mean importer -> imported. All results are heuristic, not runtime guarantees.
export function impactFor(report, target, {maxDepth=20}={}){
 const files=Array.isArray(report?.files)?report.files:[];
 const known=new Set(files.map(f=>f.name));
 if(!known.has(target))throw new Error('Choose a file from the current report.');
 const reverse=new Map(files.map(f=>[f.name,[]]));
 for(const edge of report.relationships||[]){
  if(known.has(edge.from)&&known.has(edge.to)&&edge.from!==edge.to)
   reverse.get(edge.to).push(edge.from);
 }
 for(const names of reverse.values())names.sort();
 const queue=[{file:target,depth:0,path:[target]}],visited=new Set([target]),affected=[];
 for(let cursor=0;cursor<queue.length;cursor++){
  const item=queue[cursor];
  if(item.depth>=maxDepth)continue;
  for(const name of reverse.get(item.file)){
   if(visited.has(name))continue;
   visited.add(name);
   const next={file:name,depth:item.depth+1,path:[name,...item.path]};
   affected.push(next);queue.push(next);
  }
 }
 affected.sort((a,b)=>a.depth-b.depth||a.file.localeCompare(b.file));
 const notes=(report.findings||[]).filter(f=>f.file===target);
 return {target,direct:affected.filter(x=>x.depth===1),indirect:affected.filter(x=>x.depth>1),affected,notes,scanned:files.length,scope:'detected-relative-imports-only',caveat:'Potential import impact, not runtime reachability or guaranteed breakage.'};
}
export function searchProject(report,query){
 const q=String(query||'').trim().toLocaleLowerCase().slice(0,120);
 if(!q)return [];
 const files=Array.isArray(report?.files)?report.files:[];
 const hits=[];
 for(const f of files){
  const n=f.name.toLocaleLowerCase(),type=f.extension.toLocaleLowerCase();
  if(n.includes(q)||type===q)hits.push({kind:'file',file:f.name,title:f.name,detail:f.extension+' · '+f.lines+' lines',score:n===q?0:n.startsWith(q)?1:2});
 }
 for(const f of report?.findings||[]){
  const title=f.title.toLocaleLowerCase(),help=f.help.toLocaleLowerCase();
  if(title.includes(q)||help.includes(q)||f.id.includes(q))hits.push({kind:'note',file:f.file,title:f.title,detail:f.file+' · line '+f.line+' · '+f.severity,score:3});
 }
 return hits.sort((a,b)=>a.score-b.score||a.title.localeCompare(b.title)).slice(0,30);
}
export function exportImpact(report,target){
 const impact=impactFor(report,target);
 return {product:'Asko',version:'v3-preview',generatedAt:new Date().toISOString(),target,scope:impact.scope,caveat:impact.caveat,affected:impact.affected.map(({file,depth,path})=>({file,depth,path})),notes:impact.notes.map(({id,severity,title,file,line})=>({id,severity,title,file,line})),containsSourceCode:false};
}

