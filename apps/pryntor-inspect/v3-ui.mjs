import {impactFor,searchProject,exportImpact} from './v3-model.mjs';
const $=id=>document.getElementById(id);
const e=(tag,cls,content)=>{
 const node=document.createElement(tag);if(cls)node.className=cls;if(content!==undefined)node.textContent=content;return node;
};
let report=null,selected=null;
const pick=$('v3Target'),search=$('v3Search'),searchResults=$('v3SearchResults'),impactList=$('v3ImpactList'),summary=$('v3Summary');
function jump(name){
 const index=report?.files.findIndex(f=>f.name===name);
 if(index<0)return;
 $('fileQuery').value='';
 $('fileQuery').dispatchEvent(new Event('input',{bubbles:true}));
 const row=$('fileRows').children[index];
 row?.click();
 $('fileDetail').scrollIntoView({behavior:'smooth',block:'center'});
}
function renderSearch(){
 searchResults.replaceChildren();
 if(!report)return;
 const hits=searchProject(report,search.value);
 if(!search.value.trim()){searchResults.append(e('p','v3-empty','Search file names, extensions, or review-note titles.'));return;}
 if(!hits.length){searchResults.append(e('p','v3-empty','No matching file names or review notes in this local report.'));return;}
 for(const hit of hits){
  const btn=e('button','v3-hit');btn.type='button';
  const badge=e('span','v3-hit-kind',hit.kind==='file'?'FILE':'NOTE');
  const copy=e('span','v3-hit-copy');copy.append(e('strong',null,hit.title),e('small',null,hit.detail));
  btn.append(badge,copy,e('span','v3-hit-arrow','↗'));
  btn.addEventListener('click',()=>jump(hit.file));
  searchResults.append(btn);
 }
}
function renderImpact(){
 impactList.replaceChildren();
 if(!report||!selected)return;
 const result=impactFor(report,selected);
 const count=result.affected.length;
 summary.textContent=count+' potentially affected file'+(count===1?'':'s')+' · '+result.direct.length+' direct · '+result.indirect.length+' transitive · '+result.notes.length+' notes in selected file';
 const top=e('div','v3-impact-origin');
 top.append(e('span','v3-origin-tag','SELECTED MODULE'),e('strong',null,selected));
 impactList.append(top);
 if(!count)impactList.append(e('p','v3-empty','No other selected files import this module through the detected relative-import graph. Other runtime relationships may exist.'));
 for(const entry of result.affected){
  const row=e('button','v3-impact-item');row.type='button';
  row.append(e('span','v3-impact-step',entry.depth===1?'DIRECT':'+'+entry.depth));
  const copy=e('span','v3-impact-copy');copy.append(e('strong',null,entry.file),e('small',null,entry.path.join(' → ')));
  row.append(copy,e('span','v3-hit-arrow','↗'));
  row.addEventListener('click',()=>jump(entry.file));impactList.append(row);
 }
}
function update(reportNext){
 report=reportNext;selected=report?.files[0]?.name||null;
 pick.replaceChildren();
 if(!report){search.value='';summary.textContent='Scan files to explore impact.';impactList.replaceChildren();searchResults.replaceChildren();return;}
 for(const f of report.files){const opt=e('option',null,f.name);opt.value=f.name;pick.append(opt);}
 pick.value=selected;renderImpact();renderSearch();
}
document.addEventListener('asko:report',event=>update(event.detail));
pick.addEventListener('change',()=>{selected=pick.value;renderImpact();});
search.addEventListener('input',renderSearch);
$('v3Export').addEventListener('click',()=>{
 if(!report||!selected)return;
 const data=exportImpact(report,selected),blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});
 const url=URL.createObjectURL(blob),link=e('a');link.href=url;link.download='asko-impact-report.json';link.click();
 setTimeout(()=>URL.revokeObjectURL(url),1000);
});
$('v3SearchClear').addEventListener('click',()=>{search.value='';renderSearch();search.focus();});

