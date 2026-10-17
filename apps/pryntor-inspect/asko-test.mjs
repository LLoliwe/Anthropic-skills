import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {respond} from './asko-response.mjs';
import {analyze,EXAMPLE} from './inspector.mjs';
const report=analyze(EXAMPLE,{mode:'sample'});
test('Asko remains a real local-only source inspector',()=>{
 assert.equal(report.product,'Asko');
 assert.equal(report.codeExecuted,false);
 assert.equal(report.customerDataUploaded,false);
 assert.equal(report.securityCertification,false);
 assert.equal(report.counts.files,2);
});
test('Ari truthfully declines to infer without a report',()=>{
 assert.match(respond('How do my files connect?',null),/don't have a local report/i);
});
test('Ari maps current detected static imports to grounded summary',()=>{
 const answer=respond('How do my files connect?',report);
 assert.match(answer,/1 matched local relationship/);
 assert.match(answer,/index\.js imports format\.js/i);
 assert.match(answer,/not a compiler-accurate call graph/i);
});
test('Ari notes are never described as certified security findings',()=>{
 const answer=respond('Security issues?',report);
 assert.match(answer,/heuristic/i);
 assert.match(answer,/not verified vulnerabilities/i);
});
test('Ari describes original code inventory correctly',()=>{
 const answer=respond('Project overview',report);
 assert.match(answer,/2 files/);
 assert.match(answer,/format\.js|index\.js/);
});
test('Ari truthfully identifies its non-AI operation',()=>{
 assert.match(respond('Are you an AI model?',report),/rule-based/i);
});
test('public page has interactive mascot and guide without external script',async()=>{
 const html=await readFile(new URL('./index.html',import.meta.url),'utf8');
 assert.match(html,/id="askoMascot"/);
 assert.match(html,/id="askoGuideDialog"/);
 assert.match(html,/id="askoGuideQuestion"/);
 assert.match(html,/id="askoSample"/);
 assert.match(html,/id="askoUpload"/);
 assert.match(html,/(class="ari-illustration"|src="\.\/concept-hero\.webp")/);
 assert.match(html,/connect-src 'none'/);
 assert.match(html,/src="\.\/asko-guide\.mjs"/);
 assert.doesNotMatch(html,/\bPryntor\b/i);
});
test('guide code makes no network calls and renders user text safely',async()=>{
 const guide=await readFile(new URL('./asko-guide.mjs',import.meta.url),'utf8');
 assert.doesNotMatch(guide,/\bfetch\s*\(/);
 assert.doesNotMatch(guide,/\bXMLHttpRequest\b/);
 assert.doesNotMatch(guide,/\.innerHTML\s*=/);
 assert.match(guide,/textContent=text/);
});
test('Asko is connected to V1 dependency engine, not a static screenshot',async()=>{
 const app=await readFile(new URL('./app.mjs',import.meta.url),'utf8');
 const ui=await readFile(new URL('./v1-ui.mjs',import.meta.url),'utf8');
 assert.match(app,/setupV1/);
 assert.match(app,/asko:report/);
 assert.match(ui,/buildGraphModel/);
});

