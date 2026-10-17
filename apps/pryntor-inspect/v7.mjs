// Asko V7: actual scanner metadata drives all product panes; no remote calls.
import {analyze} from './inspector.mjs';
import {CONCEPT_SAMPLES} from './concept-samples.mjs';
import {impactFor} from './v3-model.mjs';
const $=id=>document.getElementById(id),sample=analyze(CONCEPT_SAMPLES.web,{mode:'sample'});
const make=(tag,className,value)=>{const x=document.createElement(tag);if(className)x.className=className;if(value!==undefined)x.textContent=String(value);return x;};
let report=null,shown=sample,mode='map',chosen=sample.files[0].name;
const tabs={map:['v7TabMap','v7PaneMap'],impact:['v7TabImpact','v7PaneImpact'],review:['v7TabReview','v7PaneReview']};
const short=value=>String(value||'').split('/').pop();
function jump(file){
 if(!report)document.dispatchEvent(new CustomEvent('asko:load-concept-sample',{detail:'web'}));
 const index=report?.files.findIndex(f=>f.name===file)??-1;
 if(index<0)return;
 $('fileQuery').value='';$('fileQuery').dispatchEvent(new Event('input',{bubbles:true}));
 $('fileRows').children[index]?.click();$('fileDetail').scrollIntoView({behavior:'smooth'});
}
function count(){
 $('v7Count').replaceChildren(document.createTextNode(String(shown.files.length)),make('small',null,'FILES'));
 $('v7NoteCount').textContent=String(shown.findings.length);
 $('v7WindowTitle').textContent=report?'See what your files reveal.':'Understand the connections.';
 $('v7StatusText').textContent=report?'Local scan · '+shown.files.length+' files · '+shown.relationships.length+' imports':'Original example — code stays on device';
}
function renderImpact(){
 const body=$('v7ImpactBody');body.replaceChildren();
 const label=make('label',null,'Choose a file to trace its possible dependents');label.htmlFor='v7ImpactTarget';
 const select=make('select');select.id='v7ImpactTarget';
 for(const file of shown.files){const option=make('option',null,file.name);option.value=file.name;select.append(option);}
 chosen=shown.files.some(x=>x.name===chosen)?chosen:shown.files[0]?.name;
 select.value=chosen;select.addEventListener('change',()=>{chosen=select.value;renderImpact();});body.append(label,select);
 if(!chosen)return;
 const impact=impactFor(shown,chosen);
 body.append(make('p','v7-pane-caption',impact.direct.length+' direct · '+impact.indirect.length+' indirect possible dependents'));
 if(impact.affected.length===0)body.append(make('p','v7-empty','No matched relative-import dependents in the chosen files. Other relationships may exist.'));
 for(const item of impact.affected.slice(0,7)){
  const button=make('button');button.type='button';
  button.append(make('span','v7-depth',item.depth===1?'DIRECT':'+'+item.depth));
  const copy=make('span');copy.append(make('strong',null,short(item.file)),make('small',null,item.path.map(short).join(' → ')));button.append(copy);
  button.addEventListener('click',()=>jump(item.file));body.append(button);
 }
 body.append(make('p','v7-pane-caption','Heuristic relative imports only — not compiler-verified runtime reachability.'));
}
function renderReview(){
 const body=$('v7ReviewBody');body.replaceChildren();
 body.append(make('p','v7-pane-caption',shown.findings.length+' heuristic review notes. Not a security audit.'));
 if(!shown.findings.length)body.append(make('p','v7-empty','No listed patterns matched. This does not guarantee security.'));
 for(const finding of shown.findings.slice(0,9)){
  const button=make('button');button.type='button';
  button.append(make('span','v7-depth',finding.severity));
  const copy=make('span');copy.append(make('strong',null,finding.title),make('small',null,short(finding.file)+' · line '+finding.line));button.append(copy);
  button.addEventListener('click',()=>jump(finding.file));body.append(button);
 }
}
function switchTo(next,focus=false){
 mode=next;
 for(const [key,[tab,pane]] of Object.entries(tabs)){
  const current=key===next;$(tab).setAttribute('aria-selected',String(current));$(tab).tabIndex=current?0:-1;$(pane).hidden=!current;
 }
 if(next==='impact')renderImpact();if(next==='review')renderReview();
 if(focus)$(tabs[next][0]).focus();
}
for(const [key,[tab]] of Object.entries(tabs)){
 $(tab).addEventListener('click',()=>switchTo(key));
 $(tab).addEventListener('keydown',event=>{
  const order=Object.keys(tabs),i=order.indexOf(key);
  const next=event.key==='ArrowRight'?order[(i+1)%3]:event.key==='ArrowLeft'?order[(i+2)%3]:event.key==='Home'?order[0]:event.key==='End'?order[2]:null;
  if(next){event.preventDefault();switchTo(next,true);}
 });
}
$('v7OpenFull').addEventListener('click',()=>{
 if(!report)document.dispatchEvent(new CustomEvent('asko:load-concept-sample',{detail:'web'}));
 $('workspace').scrollIntoView({behavior:'smooth'});
});
document.addEventListener('asko:report',e=>{
 report=e.detail;shown=report||sample;chosen=shown.files[0]?.name||'';count();
 if(mode==='impact')renderImpact();if(mode==='review')renderReview();
 $('askoMascot').dataset.mood=report?'proud':'happy';
});
count();switchTo('map');
