import {analyze,EXAMPLE,LIMITS} from './inspector.mjs';
const $=id=>document.getElementById(id);
const filePicker=$('filePicker'),dropzone=$('dropzone'),empty=$('emptyView'),results=$('resultsView'),status=$('statusMessage');
let report=null,selection=0;
function setStatus(message=''){status.textContent=message}
function el(tag,cls,text){const x=document.createElement(tag);if(cls)x.className=cls;if(text!==undefined)x.textContent=text;return x}
function renderFile(index){
 const row=report.files[index];if(!row)return;
 selection=index;
 for(const [i,x] of [...$('fileRows').children].entries())x.classList.toggle('active',i===index);
 $('fileType').textContent=row.extension;
 const detail=$('fileDetail');detail.replaceChildren();
 detail.append(el('h5',null,row.name),el('p',null,row.label+' · '+row.bytes.toLocaleString()+' bytes'));
 const metrics=el('div','detail-grid');
 for(const [key,v] of [['Lines',row.lines],['Imports',row.imports.length],['Exports',row.exports],['Functions',row.functions]]){
   const box=el('div');box.append(el('span',null,key),el('strong',null,v.toLocaleString()));metrics.append(box);
 }
 detail.append(metrics);
 const deps=el('div','detail-imports');
 if(row.imports.length===0)deps.append(el('span',null,'No static imports identified'));
 else row.imports.forEach(x=>deps.append(el('span',null,x)));
 detail.append(deps);
}
function render(r){
 report=r;selection=0;empty.hidden=true;results.hidden=false;setStatus();
 $('reportMode').textContent=r.mode==='sample'?'INCLUDED EXAMPLE · NOT YOUR FILES':'YOUR FILES · PROCESSED LOCALLY';
 $('reportTitle').textContent=r.mode==='sample'?'A small project, made clear.':'Your project, at a glance.';
 $('reportSubtitle').textContent=r.mode==='sample'?'Original Pryntor sample, analysed in this browser.':'First-pass inventory from your selected files.';
 for(const[key,value] of [['statFiles',r.counts.files],['statLines',r.counts.lines],['statImports',r.counts.imports],['statNotes',r.counts.notes]])$(key).textContent=value.toLocaleString();
 $('fileCount').textContent=r.counts.files+' file'+(r.counts.files===1?'':'s');
 const list=$('fileRows');list.replaceChildren();
 r.files.forEach((file,i)=>{
  const btn=el('button','file-row'+(i===0?' active':''));btn.type='button';
  const symbol=el('span','file-symbol',file.extension.slice(0,4));const label=el('span','file-label');
  label.append(el('strong',null,file.name),el('span',null,file.lines+' lines · '+file.label));
  btn.append(symbol,label,el('span',null,'›'));btn.addEventListener('click',()=>renderFile(i));list.append(btn);
 });
 renderFile(0);
 const findings=$('findings');findings.replaceChildren();
 if(r.findings.length===0)findings.append(el('p','no-findings','No patterns flagged by this limited heuristic scan. That does not mean the code is vulnerability-free.'));
 for(const f of r.findings){
  const row=el('div','finding'),icon=el('span','finding-icon',f.severity==='High'?'!':f.severity==='Review'?'·':'i'),body=el('div','finding-body');
  body.append(el('h5',null,f.title+' · '+f.severity),el('p',null,f.help),el('small',null,f.file+' · line '+f.line));
  row.append(icon,body);findings.append(row);
 }
 results.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});
}
async function scanFileObjects(fileList){
 try{
  const files=Array.from(fileList);
  if(!files.length)return;
  if(files.length>LIMITS.maxFiles)throw Error('Choose no more than 20 files.');
  let total=0;
  for(const f of files){if(f.size>LIMITS.maxBytesPerFile)throw Error('Each file must be 256 KB or smaller.');total+=f.size;}
  if(total>LIMITS.maxTotalBytes)throw Error('Combined files must be 2 MB or smaller.');
  const selected=[];
  for(const f of files)selected.push({name:f.name,text:await f.text()});
  render(analyze(selected));
 }catch(e){setStatus(e.message||'Unable to read these files.');}
 finally{filePicker.value='';}
}
function openPicker(){filePicker.click()}
function showSample(){try{render(analyze(EXAMPLE,{mode:'sample'}))}catch(e){setStatus(e.message)}}
$('sampleButton').addEventListener('click',showSample);
$('heroSample').addEventListener('click',()=>{showSample();location.hash='workspace'});
dropzone.addEventListener('click',openPicker);
dropzone.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();openPicker()}});
filePicker.addEventListener('change',()=>scanFileObjects(filePicker.files));
for(const name of ['dragenter','dragover'])dropzone.addEventListener(name,event=>{event.preventDefault();dropzone.classList.add('drag-over')});
for(const name of ['dragleave','drop'])dropzone.addEventListener(name,event=>{event.preventDefault();dropzone.classList.remove('drag-over')});
dropzone.addEventListener('drop',event=>scanFileObjects(event.dataTransfer.files));
$('resetButton').addEventListener('click',()=>{report=null;empty.hidden=false;results.hidden=true;setStatus();$('fileRows').replaceChildren();$('fileDetail').replaceChildren();$('findings').replaceChildren();filePicker.value='';dropzone.focus()});
$('exportButton').addEventListener('click',()=>{
 if(!report)return;
 const blob=new Blob([JSON.stringify(report,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');
 a.href=url;a.download='pryntor-inspect-report.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
