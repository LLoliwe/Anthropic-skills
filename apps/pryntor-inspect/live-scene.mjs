import {analyze} from './inspector.mjs';
import {CONCEPT_SAMPLES} from './concept-samples.mjs';
const $=id=>document.getElementById(id);
const ns='http://www.w3.org/2000/svg';
const make=(tag,cls,text)=>{const x=document.createElement(tag);if(cls)x.className=cls;if(text!==undefined)x.textContent=text;return x;};
const makeSvg=(tag,attrs)=>{const el=document.createElementNS(ns,tag);for(const [key,value] of Object.entries(attrs))el.setAttribute(key,String(value));return el;};
const canvas=$('v5GraphNodes'),wires=$('v5GraphWires'),graphTitle=$('v5GraphTitle'),graphMode=$('v5GraphMode'),status=$('v5GraphStatus'),mascot=$('askoMascot');
let report=null,chosen=0,displayReport=analyze(CONCEPT_SAMPLES.web,{mode:'sample'}),demoTimer=null,demoStep=0;
const positions=[{x:24,y:50},{x:74,y:23},{x:74,y:78},{x:49,y:91},{x:45,y:7}];
const filename=name=>String(name).split('/').pop();
const nodeColor=['#cde5d3','#d1baff','#e8d9a4','#a9d0f6','#fed0cb'];
function renderGraph(current,preview=false){
 const data=current||displayReport;
 const files=Array.isArray(data.files)?data.files.slice(0,5):[];
 const relationships=Array.isArray(data.relationships)?data.relationships:[];
 canvas.replaceChildren();wires.replaceChildren();
 graphTitle.textContent=data.sampleId?data.sampleId+' / sample':preview?'web-app / src':'Your selected files';
 graphMode.textContent=preview?'SAMPLE':data.mode==='sample'?'DEMO':'LOCAL';
 if(!files.length){status.textContent='Choose local files to explore connections';return;}
 if(chosen>=files.length)chosen=0;
 const lookup=new Map(files.map((f,i)=>[f.name,i]));
 for(let i=0;i<files.length;i++){
  const p=positions[i];
  const file=files[i],button=make('button','v5-node');
  button.type='button';button.style.left=p.x+'%';button.style.top=p.y+'%';
  button.setAttribute('aria-label','Inspect '+file.name+'; '+file.lines+' lines');
  button.dataset.selected=String(i===chosen);
  const badge=make('span','v5-node-icon',String(file.extension||'JS').slice(0,2));
  badge.style.color=i===chosen?'#384758':nodeColor[i];
  const copy=make('span','v5-node-copy');
  copy.append(make('strong',null,filename(file.name)),make('small',null,file.lines+' lines'));
  button.append(badge,copy);
  button.addEventListener('click',()=>{
   chosen=i;
   if(preview){
    document.dispatchEvent(new CustomEvent('asko:load-concept-sample',{detail:'web'}));
    const index=data.files.findIndex(f=>f.name===file.name);
    queueMicrotask(()=>$('fileRows').children[index]?.click());
   }else{
    const index=(report||data).files.findIndex(f=>f.name===file.name);
    if(index!==-1)$('fileRows').children[index]?.click();
   }
   // Sample loading fires asko:report synchronously; preserve the tapped node after that reset.
   chosen=i;
   renderGraph(report||data,false);
   status.textContent='Selected '+filename(file.name)+' · '+file.imports.length+' detected imports';
  });
  canvas.append(button);
 }
 relationships.forEach((edge,i)=>{
  const a=lookup.get(edge.from),b=lookup.get(edge.to);
  if(a===undefined||b===undefined)return;
  const p=positions[a],q=positions[b],x1=p.x*4,y1=p.y*2.65,x2=q.x*4,y2=q.y*2.65;
  const curve=(x1+x2)/2,mid=(y1+y2)/2;
  const path=makeSvg('path',{d:'M '+x1+' '+y1+' Q '+curve+' '+(mid-16)+' '+x2+' '+y2,class:'v5-wire v5-wire-'+['one','two','three'][i%3]});
  wires.append(path);
  const dot=makeSvg('circle',{cx:curve,cy:mid-8,r:3,class:'v5-wire-dot'});
  wires.append(dot);
 });
 const picked=files[chosen];
 status.textContent=preview?'Interactive sample · click a file to load':filename(picked.name)+' · '+picked.imports.length+' detected imports';
}
document.addEventListener('asko:report',event=>{
 report=event.detail;chosen=0;
 if(report)renderGraph(report,false);
 else renderGraph(displayReport,true);
});
renderGraph(displayReport,true);
let lastPointer=0;
mascot.addEventListener('pointermove',event=>{
 if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;
 const now=performance.now();if(now-lastPointer<24)return;lastPointer=now;
 const box=mascot.getBoundingClientRect(),x=Math.max(-1,Math.min(1,(event.clientX-box.left)/box.width*2-1)),y=Math.max(-1,Math.min(1,(event.clientY-box.top)/box.height*2-1));
 mascot.style.setProperty('--look-x',(x*2.7).toFixed(2)+'px');
 mascot.style.setProperty('--look-y',(y*1.8).toFixed(2)+'px');
 mascot.style.setProperty('--v5-parallax-x',(x*2).toFixed(2)+'px');
 mascot.style.setProperty('--v5-parallax-y',(y*1.4).toFixed(2)+'px');
});
mascot.addEventListener('pointerleave',()=>{
 for(const [key,val] of [['--look-x','0px'],['--look-y','0px'],['--v5-parallax-x','0px'],['--v5-parallax-y','0px']])mascot.style.setProperty(key,val);
});
const demoPlay=$('askoDemoCard'),demoIcon=$('v5PlayIcon'),demoCounter=$('v5DemoCounter'),demoSubtitle=$('v5DemoSubtitle'),demoMessage=$('v5DemoMessage'),demoStage=$('v5DemoStage'),demoFile=$('v5DemoFileName');
const steps=[
 {file:'main.ts',message:'3 source files analysed on this device',subtitle:'01 · Local inventory'},
 {file:'utils.ts',message:'2 import connections detected',subtitle:'02 · Follow real imports'},
 {file:'profile.ts',message:'1 follow-up note worth reviewing',subtitle:'03 · Review suggestions'}
];
function showStep(step){
 demoStep=step%steps.length;
 const item=steps[demoStep];
 demoStage.dataset.step=String(demoStep);
 demoCounter.textContent=String(demoStep+1).padStart(2,'0')+' / 03';
 demoSubtitle.textContent=item.subtitle;
 demoFile.textContent=item.file;
 demoMessage.textContent=item.message;
 demoStage.querySelectorAll('.v5-demo-target').forEach((n,i)=>n.style.background=i===demoStep%2?'#3a7268':'#2c5557');
}
function stopDemo(){
 if(demoTimer!==null){clearInterval(demoTimer);demoTimer=null;}
 demoPlay.setAttribute('aria-pressed','false');demoPlay.setAttribute('aria-label','Play code scan demonstration');demoIcon.textContent='▶';
}
function startDemo(){
 if(demoTimer!==null){stopDemo();return;}
 showStep(0);
 demoPlay.setAttribute('aria-pressed','true');demoPlay.setAttribute('aria-label','Pause code scan demonstration');demoIcon.textContent='Ⅱ';
 if(!matchMedia('(prefers-reduced-motion: reduce)').matches)demoTimer=setInterval(()=>showStep((demoStep+1)%steps.length),2350);
}
demoPlay.addEventListener('click',startDemo);
$('v5DemoNext').addEventListener('click',()=>{showStep((demoStep+1)%steps.length);});
document.addEventListener('visibilitychange',()=>{if(document.hidden)stopDemo();});
document.addEventListener('asko:report',event=>{if(!event.detail)stopDemo();});

