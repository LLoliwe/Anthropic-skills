import {buildGraphModel,filterReviewItems} from './v1-model.mjs';
const NS='http://www.w3.org/2000/svg';
const $=id=>document.getElementById(id);
function svg(tag,attrs={},label){
 const element=document.createElementNS(NS,tag);
 for(const [k,v] of Object.entries(attrs))element.setAttribute(k,String(v));
 if(label!==undefined)element.textContent=label;
 return element;
}
export function setupV1({getReport,selectFile,runSample,resetWorkspace,exportReport,openPicker}){
 let graph=null,selected=0,level='all',query='',commandIndex=0,previousFocus=null;
 const modal=$('commandDialog'),search=$('commandSearch'),results=$('commandResults');
 function choose(index,scroll=true){
  const report=getReport();if(!report||!report.files[index])return;
  $('fileQuery').value='';filterFiles();selectFile(index);
  if(scroll)$('fileDetail').scrollIntoView({block:'nearest'});
 }
 function updateSelected(index){
  selected=index;
  if(!graph)return;
  for(const node of $('graphCanvas').querySelectorAll('[data-node-index]')){
   node.classList.toggle('selected',Number(node.getAttribute('data-node-index'))===index);
  }
  const item=graph.nodes[index];
  $('impactHint').textContent=item?
   item.dependents+' other file(s) could depend on this module through detected relative imports. Heuristic only; not a complete call graph.':
   'Select a file to see dependency context.';
  [...$('graphList').children].forEach((x,i)=>x.classList.toggle('active',i===index));
 }
 function drawGraph(){
  graph=buildGraphModel(getReport());
  const box=$('graphCanvas'),list=$('graphList');box.replaceChildren();list.replaceChildren();
  $('graphSummary').textContent=graph.nodes.length+' files · '+graph.edges.length+' detected local imports';
  if(graph.nodes.length===0){box.textContent='Choose files to see relationships.';return;}
  const picture=svg('svg',{viewBox:'0 0 '+graph.width+' '+graph.height,class:'module-svg',role:'group','aria-label':'Heuristic file relationship map'});
  const defs=svg('defs'),marker=svg('marker',{id:'pryntorArrow',viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:6,markerHeight:6,orient:'auto'});
  marker.append(svg('path',{d:'M 0 0 L 10 5 L 0 10 z',fill:'#8b96af'}));defs.append(marker);picture.append(defs);
  for(const link of graph.edges){
   const a=graph.nodes[link.from],b=graph.nodes[link.to];
   const dx=b.x-a.x,dy=b.y-a.y,d=Math.max(1,Math.hypot(dx,dy));
   picture.append(svg('line',{x1:a.x+dx/d*43,y1:a.y+dy/d*27,x2:b.x-dx/d*46,y2:b.y-dy/d*30,stroke:'#a9b5ce','stroke-width':2,'marker-end':'url(#pryntorArrow)',class:'graph-edge'}));
  }
  for(const item of graph.nodes){
   const node=svg('g',{class:'map-node',tabindex:0,role:'button','aria-label':item.id+'; '+item.dependents+' possible dependents','data-node-index':item.index});
   node.append(svg('rect',{x:item.x-59,y:item.y-30,width:118,height:63,rx:12,fill:'#fff',stroke:'#cfd8e9','stroke-width':1.5}));
   node.append(svg('text',{x:item.x,y:item.y-3,'text-anchor':'middle','font-size':12,'font-weight':700,fill:'#242b43'},item.label.length>16?item.label.slice(0,13)+'…':item.label));
   node.append(svg('text',{x:item.x,y:item.y+15,'text-anchor':'middle','font-size':10,fill:'#8590a5'},item.outgoing+' out · '+item.incoming+' in'));
   node.addEventListener('click',()=>choose(item.index));
   node.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();choose(item.index)}});
   picture.append(node);
   const button=document.createElement('button');button.type='button';button.className='graph-list-item';
   button.textContent=item.id;
   const count=document.createElement('span');count.textContent=item.dependents+' dependents';button.append(count);
   button.addEventListener('click',()=>choose(item.index));list.append(button);
  }
  box.append(picture);updateSelected(selected);
 }
 function filterFiles(){
  const report=getReport();if(!report)return;
  const term=$('fileQuery').value.trim().toLocaleLowerCase();let shown=0;
  [...$('fileRows').children].forEach((button,index)=>{
   const visible=report.files[index].name.toLocaleLowerCase().includes(term);
   button.hidden=!visible;if(visible)shown++;
  });
  $('fileSearchStatus').textContent=shown+' of '+report.files.length+' shown';
 }
 function filterFindings(){
  const report=getReport();if(!report)return;
  const hits=filterReviewItems(report.findings,{level,query});
  const allowed=new Set(hits);
  [...$('findings').children].forEach((element,index)=>{
   if(report.findings.length)element.hidden=!allowed.has(report.findings[index]);
  });
  $('reviewCount').textContent=hits.length+' of '+report.findings.length+' shown';
  $('reviewEmpty').hidden=hits.length!==0||report.findings.length===0;
  document.querySelectorAll('[data-review-level]').forEach(button=>{
   const active=button.dataset.reviewLevel===level;
   button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active));
  });
 }
 function actions(){
  const report=getReport();
  const list=[
   {title:'Try an original sample',sub:'Explore without uploading',key:'S',run:runSample},
   {title:'Choose local source files',sub:'Read owned source in your browser',key:'U',run:openPicker}
  ];
  if(report){
   list.push({title:'Find a file',sub:'Search your scanned files',key:'F',run:()=>{$('fileQuery').focus();$('fileQuery').scrollIntoView({block:'center'});}});
   list.push({title:'Explore dependencies',sub:'Open the local relationship map',key:'G',run:()=>$('architecturePanel').scrollIntoView({block:'start'})});
   list.push({title:'Review findings',sub:'Filter by severity and file',key:'R',run:()=>$('reviewToolbar').scrollIntoView({block:'center'})});
   list.push({title:'Export local JSON',sub:'Download the current report',key:'E',run:exportReport});
   list.push({title:'New local scan',sub:'Clear current analysis',key:'N',run:resetWorkspace});
   report.files.forEach((file,index)=>list.push({title:file.name,sub:file.extension+' · '+file.lines+' lines',key:'↵',run:()=>choose(index)}));
  }
  return list;
 }
 function drawActions(){
  const term=search.value.trim().toLocaleLowerCase();
  const list=actions().filter(item=>!term||(item.title+' '+item.sub).toLocaleLowerCase().includes(term)).slice(0,35);
  commandIndex=Math.min(commandIndex,Math.max(0,list.length-1));results.replaceChildren();
  list.forEach((item,index)=>{
   const button=document.createElement('button');button.type='button';
   button.className='command-option'+(index===commandIndex?' active':'');
   button.setAttribute('role','option');button.setAttribute('aria-selected',String(index===commandIndex));
   const description=document.createElement('span'),title=document.createElement('strong'),sub=document.createElement('small'),key=document.createElement('kbd');
   title.textContent=item.title;sub.textContent=item.sub;key.textContent=item.key;description.append(title,sub);
   button.append(description,key);
   button.addEventListener('click',()=>execute(item));
   button.addEventListener('mouseenter',()=>{commandIndex=index;markAction();});
   results.append(button);
  });
  if(!list.length){const note=document.createElement('p');note.className='command-empty';note.textContent='No matching actions';results.append(note);}
  return list;
 }
 function markAction(){
  [...results.children].forEach((button,index)=>{
   button.classList.toggle('active',index===commandIndex);
   if(button.hasAttribute('aria-selected'))button.setAttribute('aria-selected',String(index===commandIndex));
  });
 }
 function execute(item){if(!item)return;modal.close();item.run();}
 function openCommands(){
  if(modal.open)return;
  previousFocus=document.activeElement;search.value='';commandIndex=0;modal.showModal();drawActions();search.focus();
 }
 $('quickActionsButton').addEventListener('click',openCommands);
 $('headerCommandButton').addEventListener('click',openCommands);
 $('commandClose').addEventListener('click',()=>modal.close());
 modal.addEventListener('close',()=>{if(previousFocus?.isConnected)previousFocus.focus()});
 modal.addEventListener('click',event=>{if(event.target===modal)modal.close()});
 search.addEventListener('input',()=>{commandIndex=0;drawActions()});
 search.addEventListener('keydown',event=>{
  if(['ArrowDown','ArrowUp'].includes(event.key)){
   event.preventDefault();const items=results.querySelectorAll('button');if(!items.length)return;
   commandIndex=(commandIndex+(event.key==='ArrowDown'?1:-1)+items.length)%items.length;
   markAction();items[commandIndex].scrollIntoView({block:'nearest'});
  }else if(event.key==='Enter'){event.preventDefault();execute(drawActions()[commandIndex]);}
 });
 document.addEventListener('keydown',event=>{
  if((event.metaKey||event.ctrlKey)&&event.key.toLowerCase()==='k'){
   event.preventDefault();if(modal.open)modal.close();else openCommands();return;
  }
  const t=event.target;
  const editing=t instanceof HTMLElement&&(t.matches('input,textarea,select')||t.isContentEditable);
  if(event.key==='/'&&!editing&&!modal.open){event.preventDefault();openCommands();}
 });
 $('fileQuery').addEventListener('input',filterFiles);
 $('reviewQuery').addEventListener('input',()=>{query=$('reviewQuery').value;filterFindings()});
 document.querySelectorAll('[data-review-level]').forEach(button=>button.addEventListener('click',()=>{level=button.dataset.reviewLevel;filterFindings()}));
 return {
  onReport(){
   selected=0;level='all';query='';$('fileQuery').value='';$('reviewQuery').value='';
   filterFiles();filterFindings();drawGraph();
  },
  onFileChange(index){updateSelected(index)},
  onReset(){
   graph=null;selected=0;level='all';query='';
   $('graphCanvas').replaceChildren();$('graphList').replaceChildren();$('fileQuery').value='';$('reviewQuery').value='';
  }
 };
}

