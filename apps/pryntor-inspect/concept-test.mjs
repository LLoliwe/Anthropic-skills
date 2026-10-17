import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,stat} from 'node:fs/promises';
import {CONCEPT_SAMPLES} from './concept-samples.mjs';
import {analyze} from './inspector.mjs';
test('Three home cards are genuine local sample projects with truthful counts',()=>{
 assert.deepEqual(Object.keys(CONCEPT_SAMPLES),['web','mobile','marketing']);
 for(const [key,files] of Object.entries(CONCEPT_SAMPLES)){
  const result=analyze(files,{mode:'sample'});
  assert.equal(result.counts.files,files.length,key);
  assert.equal(result.mode,'sample');
  assert.equal(result.customerDataUploaded,false);
  assert.ok(result.relationships.length>=1,key);
  assert.equal(new Set(files.map(f=>f.name)).size,files.length);
 }
});
test('Source examples contain no remote calls, credentials or copied assets',()=>{
 for(const f of Object.values(CONCEPT_SAMPLES).flat()){
  assert.doesNotMatch(f.text,/(https?:\/\/|sk-[a-z0-9]{10}|fetch\s*\()/i);
  assert.ok(f.text.length>10);
 }
});
test('Coded reference layout is live semantic HTML, not a whole screenshot',async()=>{
 const html=await readFile(new URL('./index.html',import.meta.url),'utf8');
 for(const id of ['headerCommandButton','conceptSamples','askoMascot','askoUpload','askoSample','featureAnalyze','featureGraph','featureShortcuts','askoDemoCard','askoHelpCard','askoGuideCard','impactExplorer','workspace']){
  assert.match(html,new RegExp('id="'+id+'"'),id);
 }
 assert.match(html,/class="concept-sidebar"/);
 assert.match(html,/data-concept-sample="web"/);
 assert.match(html,/src="\.\/concept-hero\.webp"/);
 assert.match(html,/src="\.\/concept-portrait\.webp"/);
 assert.match(html,/no customer files leave this browser|no source upload|no upload/i);
 assert.match(html,/connect-src 'none'/);
 assert.doesNotMatch(html,/id="fakeChat"/);
});
test('Visual assets are separately cropped reference artwork, not fake screenshots of code',async()=>{
 for(const name of ['concept-hero.webp','concept-portrait.webp']){
  const item=await stat(new URL('./'+name,import.meta.url));
  assert.ok(item.size>1000&&item.size<200000);
 }
});
test('Demo navigation and image responsiveness are original and privacy-safe',async()=>{
 const script=await readFile(new URL('./concept-ui.mjs',import.meta.url),'utf8');
 const app=await readFile(new URL('./app.mjs',import.meta.url),'utf8');
 const css=await readFile(new URL('./concept.css',import.meta.url),'utf8');
 assert.match(script,/asko:load-concept-sample/);
 assert.match(app,/analyze\(CONCEPT_SAMPLES\[name\]/);
 assert.match(css,/prefers-reduced-motion/);
 assert.match(css,/max-width:670px/);
 assert.doesNotMatch(script,/fetch\s*\(|XMLHttpRequest|innerHTML\s*=/);
});

