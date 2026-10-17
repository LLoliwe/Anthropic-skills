import {spawn} from 'node:child_process';
const LIMIT=32_000_000;
export function evidenceOf(reply){
 if(!reply)throw Error('MCP_TOOL_ERROR');
 if(reply.isError){
  const raw=(reply.content||[]).filter(p=>p?.type==='text').map(p=>String(p.text)).join(' ').slice(0,800);
  const safe=raw.replace(/(?:token|password|secret|api[_-]?key)\\s*[:=]\\s*\\S+/ig,'[redacted]').replace(/\\/[^\\s]+/g,'[path]');
  console.error('REA original-fixture-only tool error: '+safe.slice(0,550));
  throw Error('MCP_TOOL_ERROR');
 }
 const xs=[reply.structuredContent];
 for(const p of reply.content||[])if(p?.type==='text')try{xs.push(JSON.parse(p.text))}catch{}
 for(const x of xs)for(const e of [x,x?.result,x?.evidence])if(e?.operation==='analyze_javascript_application')return e;
 throw Error('MCP_EVIDENCE_MISSING');
}
export function verifyEvidence(e){
 if(e?.provider?.id!=='rea-javascript-application')throw Error('BAD_PROVIDER');
 const g=e?.normalized_result?.graph;
 if(!Array.isArray(g?.nodes)||!Array.isArray(g?.edges))throw Error('BAD_GRAPH');
 const labels=g.nodes.flatMap(n=>(n.observations||[]).map(o=>String(o.label||'')));
 if(!['index.js','format.js'].every(s=>labels.some(x=>x.includes(s))))throw Error('MISSING_MODULE');
 if(!g.edges.some(x=>x.relation==='imports'))throw Error('MISSING_IMPORT');
 return {graphNodes:g.nodes.length,graphEdges:g.edges.length,evidenceId:e.evidence_id||null};
}
export class Client{
 constructor(bin,cwd,onExit){this.bin=bin;this.cwd=cwd;this.onExit=onExit;this.id=0;this.pending=new Map();this.buf=Buffer.alloc(0);this.dead=false;this.phase='created';}
 fail(e){for(const [id,p] of this.pending){clearTimeout(p.t);p.reject(e);this.pending.delete(id)}}
 close(){if(this.dead)return;this.dead=true;this.fail(Error('MCP_CLOSED'));if(this.proc?.pid)try{process.kill(-this.proc.pid,'SIGKILL')}catch{}}
 read(chunk){
  this.buf=Buffer.concat([this.buf,chunk]);
  if(this.buf.length>LIMIT){this.close();return;}
  let n;while((n=this.buf.indexOf(10))>=0){
   const line=this.buf.subarray(0,n);this.buf=this.buf.subarray(n+1);if(!line.length)continue;
   let x;try{x=JSON.parse(line.toString('utf8'))}catch{this.close();return;}
   const p=this.pending.get(x?.id);if(!p)continue;
   clearTimeout(p.t);this.pending.delete(x.id);if(x.error)p.reject(Error('MCP_RPC_ERROR'));else p.resolve(x.result);
  }
 }
 send(method,params={},notify=false){
  if(this.dead||!this.proc||this.proc.exitCode!==null)throw Error('MCP_NOT_RUNNING');
  const msg={jsonrpc:'2.0',method,...(notify?{}:{id:++this.id,params})};
  if(notify){this.proc.stdin.write(JSON.stringify(msg)+'\n');return Promise.resolve();}
  return new Promise((resolve,reject)=>{
   const id=msg.id,t=setTimeout(()=>{this.pending.delete(id);reject(Error('MCP_TIMEOUT'));this.close()},60000);
   this.pending.set(id,{resolve,reject,t});
   try{this.proc.stdin.write(JSON.stringify(msg)+'\n')}catch{clearTimeout(t);this.pending.delete(id);reject(Error('MCP_WRITE_FAILED'))}
  });
 }
 async start(dir){
  this.proc=spawn(this.bin,['mcp'],{cwd:this.cwd,stdio:['pipe','pipe','pipe'],detached:true,env:{...process.env,NO_COLOR:'1'}});
  this.proc.stdout.on('data',b=>this.read(b));this.proc.stderr.resume();
  this.proc.on('error',()=>this.fail(Error('MCP_SPAWN_FAILED')));
  this.proc.on('exit',(code,signal)=>{this.fail(Error('MCP_EXIT_'+(signal||code)+'_PHASE_'+this.phase));if(!this.dead)this.onExit()});
  this.phase='initialize';const hello=await this.send('initialize',{protocolVersion:'2025-03-26',capabilities:{},clientInfo:{name:'pryntor-rea-host',version:'0.1.0'}});
  if(!hello?.protocolVersion)throw Error('BAD_HELLO');
  await this.send('notifications/initialized',{},true);
  this.phase='tools_list';const tools=await this.send('tools/list',{});
  if(!Array.isArray(tools?.tools)||!tools.tools.some(t=>t.name==='analyze_javascript_application'))throw Error('TOOL_MISSING');
  this.phase='tools_call';const reply=await this.send('tools/call',{name:'analyze_javascript_application',arguments:{input_path:dir,format:'directory'}});
  return {toolCount:tools.tools.length,...verifyEvidence(evidenceOf(reply))};
 }
}
