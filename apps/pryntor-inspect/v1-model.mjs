// Pryntor Inspect V1 · offline, deterministic, heuristic relationship model.
// No resolver or dependency here requires network, FS access or source execution.
const EXTENSIONS=['','.js','.mjs','.cjs','.jsx','.ts','.tsx','.json','/index.js','/index.ts','/index.tsx'];
export function normalizeProjectPath(name){
  if(typeof name!=='string')return null;
  const parts=[];
  for(const part of name.replace(/\\/g,'/').split('/')){
    if(part===''||part==='.')continue;
    if(part==='..'){if(!parts.length)return null;parts.pop();continue;}
    parts.push(part);
  }
  return parts.join('/');
}
export function resolveLocalImport(from,target,allNames){
  if(typeof from!=='string'||typeof target!=='string'||!target.startsWith('.'))return null;
  const folder=from.includes('/')?from.slice(0,from.lastIndexOf('/')+1):'';
  const normalized=normalizeProjectPath(folder+target);
  if(!normalized)return null;
  const names=allNames instanceof Set?allNames:new Set(allNames);
  for(const ending of EXTENSIONS){const candidate=normalized+ending;if(names.has(candidate))return candidate;}
  return null;
}
export function buildGraphModel(report){
  const input=Array.isArray(report?.files)?report.files:[];
  const files=input.slice(0,20).map((f,i)=>({id:String(f.name),label:String(f.name).split('/').pop(),index:i}));
  const indices=new Map(files.map((f,i)=>[f.id,i]));
  const n=files.length,columns=Math.min(4,Math.max(1,Math.ceil(Math.sqrt(n*1.55)))),rows=Math.max(1,Math.ceil(n/columns));
  const width=640,height=Math.max(250,rows*114+42);
  const marginX=75,usable=width-2*marginX;
  const nodes=files.map((f,i)=>{
    const col=i%columns,row=Math.floor(i/columns);
    return {...f,x:columns===1?width/2:marginX+(col*usable)/(columns-1),y:82+row*114};
  });
  const raw=Array.isArray(report?.relationships)?report.relationships:[];
  const seen=new Set(),edges=[];
  for(const link of raw){
    const from=indices.get(link.from),to=indices.get(link.to);
    if(from===undefined||to===undefined||from===to)continue;
    const key=from+':'+to;if(seen.has(key))continue;
    seen.add(key);edges.push({from,to});
  }
  const incoming=nodes.map(()=>0),outgoing=nodes.map(()=>0);
  for(const e of edges){outgoing[e.from]++;incoming[e.to]++;}
  const dependentsOf=id=>{
    const target=indices.get(id);if(target===undefined)return 0;
    const visited=new Set([target]),stack=[target];
    while(stack.length){const t=stack.pop();for(const edge of edges){if(edge.to===t&&!visited.has(edge.from)){visited.add(edge.from);stack.push(edge.from);}}}
    return visited.size-1;
  };
  return {width,height,nodes:nodes.map((node,i)=>({...node,incoming:incoming[i],outgoing:outgoing[i],dependents:dependentsOf(node.id)})),edges,method:'heuristic-static-relative-imports',preciseNavigation:false};
}
export function filterReviewItems(items,{level='all',query=''}={}){
  const q=String(query).toLocaleLowerCase().trim();
  return (Array.isArray(items)?items:[]).filter(item=>(level==='all'||item.severity===level)&&(!q||[item.title,item.file,item.help,String(item.line)].some(x=>String(x).toLocaleLowerCase().includes(q))));
}

