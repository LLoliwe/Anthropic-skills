import {resolveLocalImport} from './v1-model.mjs';
export const LIMITS=Object.freeze({maxFiles:20,maxBytesPerFile:256*1024,maxTotalBytes:2*1024*1024});
const ALLOWED=/\.(?:js|mjs|cjs|jsx|ts|tsx|json|html|css)$/i;
const kind=name=>{const match=/\.([a-z0-9]+)$/i.exec(name);return match?match[1].toUpperCase():'FILE'};
const IMPORT_PATTERNS=[/\b(?:import|export)\s+(?:[\s\S]{0,100}?\s+from\s+)?['"]([^'"]+)['"]/g,/\brequire\s*\(\s*['"]([^'"]+)['"]\s*\)/g,/\bimport\s*\(\s*['"]([^'"]+)['"]\s*\)/g];
const RULES=[
  {id:'dynamic-eval',severity:'High',title:'Dynamic code execution',pattern:/\beval\s*\(|\bnew\s+Function\s*\(/g,help:'Dynamic evaluation may create security and maintenance risks. Verify intent and inputs.'},
  {id:'dom-html',severity:'Review',title:'HTML assignment',pattern:/\.innerHTML\s*=|\.outerHTML\s*=/g,help:'Review how content reaches the DOM and whether untrusted values are escaped.'},
  {id:'possible-secret',severity:'Review',title:'Potential embedded credential',pattern:/\b(?:api[_-]?key|secret|password|access[_-]?token)\s*[:=]\s*['"\x60][^\n'"\x60]{8,}['"\x60]/gi,help:'Check whether this is a real credential. Avoid distributing live secrets in source.'},
  {id:'insecure-url',severity:'Review',title:'Insecure HTTP reference',pattern:/\bhttp:\/\/[^\s'"\x60)<>]+/gi,help:'Confirm that plain HTTP is appropriate for this environment. Localhost may be intentional.'},
  {id:'debugger',severity:'Info',title:'Debugger statement',pattern:/\bdebugger\s*;/g,help:'Confirm this debugging statement should ship.'},
  {id:'todo',severity:'Info',title:'Follow-up marker',pattern:/\b(?:TODO|FIXME)\b/g,help:'Track any unfinished work separately.'}
];
const labelFor=(name,ext)=>ext==='HTML'?'Markup':ext==='CSS'?'Stylesheet':ext==='JSON'?'Data':'Source';
const sources=files=>files.map(f=>({name:f.name,text:f.text,bytes:new TextEncoder().encode(f.text).length}));
function lineAt(text,index){let n=1;for(let i=0;i<index;i++)if(text.charCodeAt(i)===10)n++;return n;}
export function analyze(files,{mode='local'}={}){
  if(!Array.isArray(files)||files.length<1)throw Error('Choose at least one supported source file.');
  if(files.length>LIMITS.maxFiles)throw Error('Choose 20 files or fewer.');
  const input=sources(files);
  let total=0;
  for(const f of input){
    if(typeof f.name!=='string'||!ALLOWED.test(f.name)||typeof f.text!=='string')throw Error('Only JS, TS, HTML, CSS and JSON source files are supported.');
    if(f.bytes>LIMITS.maxBytesPerFile)throw Error('Each file must be 256 KB or smaller.');
    total+=f.bytes;
  }
  if(total>LIMITS.maxTotalBytes)throw Error('Combined files must be 2 MB or smaller.');
  const names=new Set(),findings=[];
  const rows=input.map(f=>{
    let clean=f.name.replace(/\\/g,'/');
    if(clean.length>180)clean=clean.slice(-180);
    if(names.has(clean))throw Error('Two files share the same name. Rename one before scanning.');
    names.add(clean);
    const extension=kind(clean),lines=f.text.length?f.text.split(/\r\n|\r|\n/).length:0;
    let imports=[];
    if(!['HTML','CSS','JSON'].includes(extension)){
      for(const pattern of IMPORT_PATTERNS){pattern.lastIndex=0;for(const match of f.text.matchAll(pattern))imports.push(match[1]);}
      imports=[...new Set(imports)].slice(0,100);
    }
    if(extension==='JSON')try{JSON.parse(f.text)}catch{findings.push({id:'invalid-json',severity:'Review',title:'JSON could not be parsed',file:clean,line:1,help:'Check the JSON syntax. The file was not executed.'});}
    if(!['HTML','CSS','JSON'].includes(extension)){
      for(const rule of RULES){rule.pattern.lastIndex=0;let count=0;for(const match of f.text.matchAll(rule.pattern)){findings.push({id:rule.id,severity:rule.severity,title:rule.title,file:clean,line:lineAt(f.text,match.index),help:rule.help});if(++count>=5)break;}}
    }
    const exportCount=(f.text.match(/\bexport\s+(?:default\s+)?(?:const|function|class|interface|type|let|var|\{)/g)||[]).length+(f.text.match(/\bmodule\.exports\s*=/g)||[]).length;
    const functionCount=(f.text.match(/\bfunction\s+\w+\s*\(|(?:const|let)\s+\w+\s*=\s*(?:async\s*)?\([^)]*\)\s*=>/g)||[]).length;
    return {name:clean,extension,label:labelFor(clean,extension),lines,bytes:f.bytes,imports,exports:exportCount,functions:functionCount};
  });
  const known=new Set(rows.map(f=>f.name));
  const edges=[];
  for(const file of rows)for(const target of file.imports){
    if(!target.startsWith('.'))continue;
    const resolved=resolveLocalImport(file.name,target,known);
    if(resolved&&resolved!==file.name)edges.push({from:file.name,to:resolved,type:'imports'});
  }
  const counts={files:rows.length,lines:rows.reduce((s,f)=>s+f.lines,0),imports:rows.reduce((s,f)=>s+f.imports.length,0),notes:findings.length,bytes:total};
  return {product:'Pryntor Inspect',version:'v1-preview',method:'local-heuristic-source-inventory',mode,scope:'first-pass-only',customerDataUploaded:false,codeExecuted:false,securityCertification:false,generatedAt:new Date().toISOString(),counts,files:rows,relationships:edges,findings,limitations:['Static heuristic scan; no AST/runtime execution.','No formal security audit or REA MCP analysis.','Pattern matches may include false positives and omit true defects.']};
}
export const EXAMPLE=[
 {name:'index.js',text:"import { format } from './format.js';\n// Original Pryntor demo — no network calls\nexport function status() {\n  return format('ready');\n}\n"},
 {name:'format.js',text:"export function format(value) {\n  return 'Pryntor-' + value;\n}\n// TODO: add input validation\n"}
];
