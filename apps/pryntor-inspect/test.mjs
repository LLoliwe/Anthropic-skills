import {test} from 'node:test';
import assert from 'node:assert/strict';
import {analyze,EXAMPLE,LIMITS} from './inspector.mjs';
test('example produces truthful module relationships and counts',()=>{
 const r=analyze(EXAMPLE,{mode:'sample'});assert.equal(r.counts.files,2);assert.equal(r.counts.imports,1);
 assert.deepEqual(r.relationships.map(({from,to,type})=>({from,to,type})),[{from:'index.js',to:'format.js',type:'imports'}]);
 assert.equal(r.codeExecuted,false);assert.equal(r.customerDataUploaded,false);assert.equal(r.securityCertification,false);
});
test('security patterns are labelled review suggestions with line references',()=>{
 const r=analyze([{name:'unsafe.ts',text:'const a = 1;\neval(userInput);\nconst x = document.body.innerHTML = input;\n'}]);
 assert.ok(r.findings.some(f=>f.id==='dynamic-eval'&&f.line===2&&f.severity==='High'));
 assert.ok(r.findings.some(f=>f.id==='dom-html'&&f.line===3));
});
test('JSON parse errors are not hidden',()=>{
 const r=analyze([{name:'x.json',text:'{ invalid }'}]);assert.equal(r.findings[0].id,'invalid-json');
});
test('unsupported inputs fail closed',()=>{
 assert.throws(()=>analyze([{name:'app.exe',text:'a'}]),/Only JS/);
 assert.throws(()=>analyze([]),/Choose/);
 assert.throws(()=>analyze([{name:'empty.js',text:''},{name:'empty.js',text:''}]),/same name/);
});
test('input file and total byte limits',()=>{
 assert.throws(()=>analyze(Array.from({length:LIMITS.maxFiles+1},(_,i)=>({name:i+'.js',text:'ok'}))),/20 files/);
 assert.throws(()=>analyze([{name:'large.js',text:'a'.repeat(LIMITS.maxBytesPerFile+1)}]),/256 KB/);
});
test('no input file source is returned in report',()=>{
 const secret='private-example-only-TEST-NEVER-COMMIT';const r=analyze([{name:'private.js',text:'const notSourceText="'+secret+'";'}]);
 assert.equal(JSON.stringify(r).includes(secret),false);
});
test('HTML source has no inline scripts and contains CSP',async()=>{
 const fs=await import('node:fs/promises'),html=await fs.readFile(new URL('./index.html',import.meta.url),'utf8');
 assert.match(html,/Content-Security-Policy/);
 assert.doesNotMatch(html,/<script(?![^>]*src=)/);
 assert.match(html,/connect-src 'none'/);
});
test('app has no active network or raw HTML assignments',async()=>{
 const fs=await import('node:fs/promises'),script=await fs.readFile(new URL('./app.mjs',import.meta.url),'utf8');
 assert.doesNotMatch(script,/\bfetch\s*\(/);
 assert.doesNotMatch(script,/\.innerHTML\s*=/);
});
