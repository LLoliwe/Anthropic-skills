import{test}from'node:test';import assert from'node:assert/strict';import{evidenceOf,verifyEvidence}from'./mcp.mjs';
const valid=()=>({operation:'analyze_javascript_application',provider:{id:'rea-javascript-application'},evidence_id:'ev_fixture',normalized_result:{graph:{nodes:[{observations:[{label:'index.js'}]},{observations:[{label:'format.js'}]}],edges:[{relation:'imports'}]}}});
test('real envelope schema',()=>assert.equal(verifyEvidence(evidenceOf({structuredContent:valid()})).graphNodes,2));
test('text envelope',()=>assert.equal(verifyEvidence(evidenceOf({content:[{type:'text',text:JSON.stringify(valid())}]})).graphEdges,1));
test('error result fails closed',()=>assert.throws(()=>evidenceOf({isError:true}),/MCP_TOOL_ERROR/));
test('unexpected provider fails closed',()=>{const x=valid();x.provider.id='other';assert.throws(()=>verifyEvidence(x),/BAD_PROVIDER/)});
test('missing import fails closed',()=>{const x=valid();x.normalized_result.graph.edges=[];assert.throws(()=>verifyEvidence(x),/MISSING_IMPORT/)});
test('missing module fails closed',()=>{const x=valid();x.normalized_result.graph.nodes=[];assert.throws(()=>verifyEvidence(x),/MISSING_MODULE/)});
