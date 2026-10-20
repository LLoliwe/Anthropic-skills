import{test}from'node:test';import assert from'node:assert/strict';
import{normalizeProjectPath,resolveLocalImport,buildGraphModel,filterReviewItems}from'./v1-model.mjs';
test('relative path resolver handles nested folders correctly',()=>{
 const names=new Set(['src/feature/math.ts','other/math.ts','src/app.ts','src/index.ts','src/shared/index.js']);
 assert.equal(resolveLocalImport('src/app.ts','./feature/math',names),'src/feature/math.ts');
 assert.equal(resolveLocalImport('src/app.ts','../other/math',names),'other/math.ts');
 assert.equal(resolveLocalImport('src/app.ts','./shared',names),'src/shared/index.js');
 assert.equal(resolveLocalImport('src/app.ts','../../../../etc/secrets',names),null);
 assert.equal(resolveLocalImport('src/app.ts','react',names),null);
});
test('path normalization preserves roots and ignores redundant segments',()=>{
 assert.equal(normalizeProjectPath('src/./components/../app.js'),'src/app.js');
 assert.equal(normalizeProjectPath('../secrets'),null);
 assert.equal(normalizeProjectPath('x\\file.js'),'x/file.js');
});
test('graph is bounded and has deterministic edges',()=>{
 const report={files:[{name:'src/a.js'},{name:'src/b.js'},{name:'src/c.js'}],relationships:[{from:'src/a.js',to:'src/b.js'},{from:'src/b.js',to:'src/c.js'},{from:'src/a.js',to:'src/b.js'}]};
 const g=buildGraphModel(report);assert.equal(g.nodes.length,3);assert.equal(g.edges.length,2);assert.equal(g.nodes[2].dependents,2);assert.equal(g.nodes[1].incoming,1);
 assert.ok(g.nodes.every(n=>n.x>=0&&n.x<=g.width&&n.y>=0&&n.y<=g.height));
 assert.equal(g.preciseNavigation,false);
});
test('cycles do not hang or count a module as its own dependent',()=>{
 const report={files:[{name:'a.ts'},{name:'b.ts'}],relationships:[{from:'a.ts',to:'b.ts'},{from:'b.ts',to:'a.ts'}]};
 const g=buildGraphModel(report);assert.equal(g.nodes[0].dependents,1);assert.equal(g.nodes[1].dependents,1);
});
test('empty or invalid graph is benign',()=>{
 assert.deepEqual(buildGraphModel(null).nodes,[]);assert.equal(buildGraphModel({files:[{name:'a.ts'}],relationships:[{from:'not.ts',to:'a.ts'}]}).edges.length,0);
});
test('review filters preserve original objects and respond to severity/text',()=>{
 const rows=[{severity:'High',title:'Dynamic evaluation',file:'a.ts',line:2},{severity:'Review',title:'HTML injection',file:'b.ts',line:10}];
 assert.deepEqual(filterReviewItems(rows,{level:'High'}),[rows[0]]);
 assert.deepEqual(filterReviewItems(rows,{query:'b.ts'}),[rows[1]]);
 assert.deepEqual(filterReviewItems(rows,{query:'10'}),[rows[1]]);
});

