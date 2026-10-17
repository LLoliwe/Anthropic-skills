import http from 'node:http';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Client} from './mcp.mjs';
const ROOT=path.dirname(fileURLToPath(import.meta.url)),PORT=Number(process.env.PORT||10000);
if(!Number.isInteger(PORT)||PORT<1||PORT>65535)throw Error('BAD_PORT');
const state={ready:false,status:'starting',toolCount:0,graphNodes:0,graphEdges:0,evidenceId:null,checkedAt:null};
let client=null,retry=null,stopping=false;
function respond(res,code,x){const body=JSON.stringify(x);res.writeHead(code,{'content-type':'application/json','cache-control':'no-store','x-content-type-options':'nosniff','content-security-policy':"default-src 'none'"});res.end(body)}
const server=http.createServer((req,res)=>{
 if(req.method!=='GET')return respond(res,405,{error:'METHOD_NOT_ALLOWED'});
 const url=req.url?.split('?')[0];
 if(url==='/healthz')return respond(res,200,{service:'pryntor-rea-sandbox',process:'running'});
 if(url==='/readyz')return respond(res,state.ready?200:503,{...state,scope:'original-fixture-only',physicalControl:false,customerData:false});
 if(url==='/')return respond(res,200,{service:'pryntor-rea-sandbox',privilegedEndpoints:0});
 return respond(res,404,{error:'NOT_FOUND'});
});
server.requestTimeout=5000;server.headersTimeout=10000;
function schedule(){if(stopping||retry)return;retry=setTimeout(()=>{retry=null;void boot()},30000);retry.unref()}
async function boot(){
 if(stopping)return;state.ready=false;state.status='verifying';
 const c=new Client(path.join(ROOT,'node_modules','.bin','rea-agents'),ROOT,()=>{if(client===c&&!stopping){state.ready=false;state.status='mcp-exited';schedule()}});
 client=c;
 try{const result=await c.start(path.join(ROOT,'fixture'));if(stopping||client!==c)return;
  Object.assign(state,{ready:true,status:'verified',...result,checkedAt:new Date().toISOString()});
  console.log(JSON.stringify({event:'rea-fixture-verified',toolCount:result.toolCount,graphNodes:result.graphNodes,graphEdges:result.graphEdges}));
 }catch(e){const code=String(e?.message||'UNKNOWN').replace(/[^A-Za-z0-9_-]/g,'_').slice(0,90);state.ready=false;state.status='verification-failed';state.lastErrorCode=code;state.lastPhase=c.phase;c.close();schedule();console.error('REA fixture verification failed: '+code+' phase='+c.phase)}
}
server.listen(PORT,'0.0.0.0',()=>{console.log(JSON.stringify({event:'server-listening',port:PORT}));void boot()});
function shutdown(){if(stopping)return;stopping=true;if(retry)clearTimeout(retry);client?.close();server.close(()=>process.exit(0));setTimeout(()=>process.exit(0),4000).unref()}
process.on('SIGTERM',shutdown);process.on('SIGINT',shutdown);
