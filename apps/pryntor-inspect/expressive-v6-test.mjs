import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {analyze} from './inspector.mjs';
import {CONCEPT_SAMPLES} from './concept-samples.mjs';
const read=name=>readFile(new URL('./'+name,import.meta.url),'utf8');

test('V6 renders a redesigned seated vector Ari at two scales, with distinct SVG identifiers',async()=>{
 const html=await read('index.html');
 assert.equal((html.match(/<svg class="ari-illustration\b/g)||[]).length,2);
 assert.match(html,/viewBox="0 0 760 740"/);
 assert.match(html,/class="v6-loose-hair"/);
 assert.match(html,/class="v6-front-shoe"/);
 assert.match(html,/class="v6-eyes"/);
 assert.match(html,/id="v6Skin"/);
 assert.match(html,/id="miniv6Skin"/);
 assert.doesNotMatch(html,/<img\b|concept-hero\.webp|concept-portrait\.webp/i);
});
test('V6 cat is an actual keyboard button with screen reader status',async()=>{
 const html=await read('index.html');
 assert.match(html,/<button class="v6-cat-button" id="v6CatButton" type="button"/);
 assert.match(html,/aria-label="Ask the cat for a local project tip"/);
 assert.match(html,/id="v6CatBubble" role="status" aria-live="polite"/);
 const js=await read('expressive-v6.mjs');
 assert.match(js,/cat.addEventListener\('click'/);
 assert.match(js,/cat.classList.add\('is-happy'\)/);
});
test('V6 responsive CSS fixes SVG intrinsic grid sizing on desktop and mobile',async()=>{
 const css=await read('expressive-v6.css');
 assert.match(css,/@media\(min-width:671px\)/);
 assert.match(css,/\.concept-stage\{grid-template-rows:minmax\(0,1fr\)\}/);
 assert.match(css,/\.concept-art\{height:100%;max-height:100%;min-height:0/);
 assert.match(css,/@media\(max-width:390px\)/);
 assert.match(css,/prefers-reduced-motion:reduce/);
 assert.match(css,/\.v5-node\{min-height:44px!important\}/);
});
test('V6 animate particles along detected graph edges, not fake preset metrics',async()=>{
 const js=await read('expressive-v6.mjs');
 const graph=await read('live-scene.mjs');
 assert.match(js,/const paths=\[\.\.\.wires.querySelectorAll\('path.v5-wire'\)\]/);
 assert.match(js,/offsetPath='path/);
 assert.doesNotMatch(js,/animateMotion|fetch\s*\(|XMLHttpRequest|\.innerHTML\s*=/);
 assert.match(graph,/relationships.forEach\(\(edge,i\)=>/);
 assert.match(graph,/data\.files/);
 assert.match(graph,/chosen=i;\n   renderGraph\(report\|\|data,false\)/);
 const sample=analyze(CONCEPT_SAMPLES.web,{mode:'sample'});
 assert.equal(sample.files.length,3);
 assert.equal(sample.relationships.length,2);
});
test('V6 all enhancements local with original V1-V5 functionality preserved',async()=>{
 const html=await read('index.html');
 for(const identifier of ['filePicker','graphCanvas','impactExplorer','v5GraphCanvas','v5GraphNodes','askoMascot','v6CatButton','askoGuideDialog','askoDemoCard','v5DemoNext'])assert.match(html,new RegExp('id="'+identifier+'"'));
 assert.match(html,/connect-src 'none'/);
 assert.match(html,/expressive-v6\.css/);
 assert.match(html,/expressive-v6\.mjs/);
});

