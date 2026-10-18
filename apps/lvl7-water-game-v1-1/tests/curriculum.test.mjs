import test from 'node:test';
import assert from 'node:assert/strict';
import {buildGraph,pathway} from '../../../tools/learning-graph/graph.mjs';
import {starterTopics,starterEdges,filteredTopics,unlocks,labFor,verifiedJSON} from '../curriculum.mjs';
const graph=buildGraph(starterTopics,starterEdges);
test('sequence puts dependencies before the selected idea',()=>{
 const seq=pathway(graph,'boiling');assert.equal(seq.at(-1).id,'boiling');
 for(const node of seq)for(const e of graph.prereqs.get(node.id))assert(seq.findIndex(n=>n.id===e.id)<seq.findIndex(n=>n.id===node.id));
});
test('search, subject and age filters compose without matching unknown ages',()=>{
 assert.equal(filteredTopics(graph,{query:'boiling',subject:'Science',age:'7'}).length,1);
 assert.equal(filteredTopics(graph,{age:'4'}).length,0);
 assert.equal(filteredTopics(graph,{subject:'English'}).length,0);
 assert.equal(filteredTopics(graph,{query:'  WATER  '}).length,2);
});
test('unlocks reverse dependency edges',()=>assert.deepEqual(unlocks(graph,'heating').map(t=>t.id),['boiling']));
test('only reviewed related concepts link to the available experiment',()=>{
 assert(labFor('mt_Pl-nsjYGZ3',true));assert(labFor('mt_1JFUNQDwAJ',true));assert.equal(labFor('fractions',true),false);
});
test('network failures and modified source fail closed',async()=>{
 await assert.rejects(verifiedJSON('topics.json',async()=>new Response('{}',{status:404})),/failed/);
 await assert.rejects(verifiedJSON('topics.json',async()=>new Response('{}')),/checksum/);
});
