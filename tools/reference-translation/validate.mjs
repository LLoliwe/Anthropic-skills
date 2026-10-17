import fs from "node:fs"; import path from "node:path";
export function validateTrace(d, exists=()=>true){
 const e=[];if(!d||typeof d!=="object"||Array.isArray(d))return ["Root must be a JSON object"];
 const required=(x,k)=>{if(typeof x!=="string"||x.trim().length<12)e.push(k+" needs substantive text")};
 for(const k of ["venture","userTask","designDirection","interaction","dataTruth","learnerSafety","privacy","reviewState"])required(d[k],k);
 if(!Array.isArray(d.references)||d.references.length<2)e.push("At least two attributable design references required");
 else {const seen=new Set();
 for(let i=0;i<d.references.length;i++){const r=d.references[i];if(!r||typeof r!=="object"){e.push("Bad reference "+i);continue;}
 for(const k of ["creator","mechanism","originalTranslation","doNotCopy","rights"])required(r[k],"references["+i+"]."+k);
 if(!/^https:\/\//.test(r.url??""))e.push("Reference URL must be HTTPS");
 if(seen.has(r.url))e.push("Duplicate reference");seen.add(r.url);
 if(r.originalTranslation===r.mechanism)e.push("Copied mechanism cannot be its own translation");
 }}
 if(!Array.isArray(d.originalAssets)||!d.originalAssets.length)e.push("Missing original asset provenance");
 else for(const s of d.originalAssets)required(s,"originalAsset");
 for(const k of ["artifactFiles","testFiles"]){if(!Array.isArray(d[k])||!d[k].length)e.push("Missing "+k);
 else for(const f of d[k])if(typeof f!=="string"||!exists(f))e.push("Missing file "+f);}
 if(d.releaseStatus==="released"&&!d.independentApprovalEvidence)e.push("No public release claim without independent evidence");
 return e;
}
if(process.argv[1]&&path.resolve(process.argv[1])===path.resolve(new URL(import.meta.url).pathname)){
 const fp=process.argv[2];if(!fp){console.error("Expected trace JSON path");process.exitCode=2;}
 else{try{const d=JSON.parse(fs.readFileSync(fp,"utf8"));const root=path.dirname(path.resolve(fp));const e=validateTrace(d,f=>fs.existsSync(path.join(root,f)));
 if(e.length){console.error(e.join("\n"));process.exitCode=1;}else console.log("PASS original reference evidence trace; "+d.references.length+" references; status "+d.releaseStatus);
 }catch(e){console.error(e.message);process.exitCode=1;}}
}