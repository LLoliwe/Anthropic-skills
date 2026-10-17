import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {analyze} from './inspector.mjs';
import {CONCEPT_SAMPLES} from './concept-samples.mjs';

test('hero and original expressive Ari card are both real scalable vector art',async()=>{
 const html=await readFile(new URL('./index.html',import.meta.url),'utf8');
 assert.equal((html.match(/<svg class="ari-illustration ari-v8/g)||[]).length,2);
 assert.match(html,/class="ari-illustration ari-v8 ari-v8-hero"/);
 assert.match(html,/class="v5-graph-wires"/);
 assert.match(html,/id="v5GraphNodes"/);
 assert.match(html,/id="v5DemoStage"/);
 assert.match(html,/live-scene.mjs/);
 assert.match(html,/live-scene.css/);
 assert.doesNotMatch(html,/concept-(?:hero|portrait)\.webp/i);
 assert.doesNotMatch(html,/<img\b/i);
});
test('live graph draws true static imports from real demo rather than fictitious counts',()=>{
 const report=analyze(CONCEPT_SAMPLES.web,{mode:'sample'});
 assert.equal(report.files.length,3);
 assert.equal(report.relationships.length,2);
 assert.equal(report.findings.length,1);
 assert.deepEqual(report.relationships.map(e=>e.to).sort(),['web-app/profile.ts','web-app/utils.ts']);
});
test('quick demo uses same three-file fixture as its actual display',async()=>{
 const guide=await readFile(new URL('./asko-guide.mjs',import.meta.url),'utf8');
 const demo=await readFile(new URL('./live-scene.mjs',import.meta.url),'utf8');
 assert.match(guide,/askoDemoCard'\)\.addEventListener\('click',\(\)=>document\.dispatchEvent/);
 assert.match(demo,/3 source files analysed on this device/);
 assert.match(demo,/2 import connections detected/);
 assert.match(demo,/1 follow-up note worth reviewing/);
 assert.match(demo,/aria-pressed/);
});
test('vector response is touch/keyboard friendly with reduced-motion support',async()=>{
 const css=await readFile(new URL('./live-scene.css',import.meta.url),'utf8');
 assert.match(css,/\bmax-width:670px\b/);
 assert.match(css,/prefers-reduced-motion:reduce/);
 assert.match(css,/v5-ari-button:focus-visible/);
 const code=await readFile(new URL('./live-scene.mjs',import.meta.url),'utf8');
 assert.match(code,/pointermove/);
 assert.match(code,/visibilitychange/);
 assert.match(code,/renderGraph\(report,false\)/);
 assert.doesNotMatch(code,/\bfetch\s*\(|\.innerHTML\s*=/);
});

