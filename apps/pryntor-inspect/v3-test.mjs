import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {impactFor,searchProject,exportImpact} from './v3-model.mjs';
const files=['entry.ts','mid.ts','core.ts','other.ts','solo.ts'].map(name=>({name,extension:'TS',lines:2}));
const report={files,relationships:[{from:'entry.ts',to:'mid.ts'},{from:'mid.ts',to:'core.ts'},{from:'other.ts',to:'core.ts'},{from:'core.ts',to:'mid.ts'}],findings:[{id:'dynamic-eval',title:'Dynamic code execution',severity:'High',file:'core.ts',line:4,help:'Review'}]};
test('reverse import traversal finds direct and transitive impact',()=>{
 const r=impactFor(report,'core.ts');
 assert.deepEqual(r.direct.map(x=>x.file),['mid.ts','other.ts']);
 assert.deepEqual(r.indirect.map(x=>x.file),['entry.ts']);
 assert.deepEqual(r.indirect[0].path,['entry.ts','mid.ts','core.ts']);
});
test('cycles terminate and each module appears once',()=>{
 const r=impactFor(report,'mid.ts');
 assert.deepEqual(r.affected.map(x=>x.file),['core.ts','entry.ts','other.ts']);
 assert.equal(new Set(r.affected.map(x=>x.file)).size,3);
});
test('unknown module rejected and zero dependents explicit',()=>{
 assert.throws(()=>impactFor(report,'unknown.ts'),/Choose a file/);
 assert.equal(impactFor(report,'solo.ts').affected.length,0);
});
test('impact export omits source and retains provenance',()=>{
 const data=exportImpact(report,'core.ts');
 assert.equal(data.containsSourceCode,false);
 assert.equal(data.affected.length,3);
 assert.equal(data.notes.length,1);
 assert.ok(!JSON.stringify(data).includes('rawSource'));
 assert.match(data.caveat,/not runtime reachability/);
});
test('local quick find searches only report metadata',()=>{
 assert.deepEqual(searchProject(report,'mid').map(x=>x.file),['mid.ts']);
 assert.equal(searchProject(report,'dynamic')[0].kind,'note');
 assert.equal(searchProject(report,'no such match').length,0);
 assert.equal(searchProject(report,'').length,0);
});
test('workbench is connected and respects strict no-network policy',async()=>{
 const html=await readFile(new URL('./index.html',import.meta.url),'utf8');
 const ui=await readFile(new URL('./v3-ui.mjs',import.meta.url),'utf8');
 assert.match(html,/id="impactExplorer"/);
 assert.match(html,/id="v3Target"/);
 assert.match(html,/id="v3Search"/);
 assert.match(html,/v3-ui.mjs/);
 assert.match(html,/connect-src 'none'/);
 assert.match(ui,/asko:report/);
 assert.doesNotMatch(ui,/\bfetch\s*\(|\.innerHTML\s*=/);
});

