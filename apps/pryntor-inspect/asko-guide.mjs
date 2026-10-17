// Asko V2: local-only, deterministic guide with no HTTP calls or AI-provider claims.
const $=id=>document.getElementById(id);
let report=null,previousFocus=null,tipNumber=0;
const dialog=$('askoGuideDialog'),history=$('askoGuideHistory'),form=$('askoGuideForm'),input=$('askoGuideQuestion'),portrait=$('askoMascot');
const tips=[
 "Hi! I'm Ari. Try the sample, then ask me about files, relationships or review notes.",
 "Your source files stay on this device. I help you navigate the summary.",
 "Tip: press Ctrl or ⌘ + K to find a file or action, or / for the command menu.",
 "I can explain detected imports and flagged patterns. I can't verify runtime behaviour."
];
import {respond} from './asko-response.mjs';
function addMessage(role,text){
 const row=document.createElement('div');row.className='guide-message '+role;
 const label=document.createElement('span');label.className='guide-message-label';label.textContent=role==='ari'?'Ari':'You';
 const p=document.createElement('p');p.textContent=text;row.append(label,p);history.append(row);history.scrollTop=history.scrollHeight;
}
function ask(text){
 const question=String(text||'').trim();if(!question)return;
 addMessage('user',question);addMessage('ari',respond(question,report));
 portrait.dataset.mood=report?'proud':'curious';
 setTimeout(()=>{if(portrait.dataset.mood!=='sleeping')portrait.dataset.mood='happy';},1100);
}
function openGuide(){
 if(dialog.open)return;
 previousFocus=document.activeElement;dialog.showModal();
 if(!history.children.length)addMessage('ari',tips[0]);
 portrait.dataset.mood='happy';input.focus();
}
function closeGuide(){if(dialog.open)dialog.close();}
function sample(){$('sampleButton').click();portrait.dataset.mood='proud';}
$('askoUpload').addEventListener('click',()=>$('filePicker').click());
$('askoSample').addEventListener('click',sample);
$('askoDemoCard').addEventListener('click',sample);
$('featureAnalyze').addEventListener('click',()=>{if(!$('resultsView').hidden)$('workspace').scrollIntoView({behavior:'smooth'});else sample();});
$('featureGraph').addEventListener('click',()=>{if(!$('resultsView').hidden)$('architecturePanel').scrollIntoView({block:'center',behavior:'smooth'});else sample();});
$('featureShortcuts').addEventListener('click',()=>$('headerCommandButton').click());
for(const id of ['askoGuideFab','askoGuideCard','askoHelpCard'])$(id).addEventListener('click',openGuide);
portrait.addEventListener('click',()=>{tipNumber=(tipNumber+1)%tips.length;openGuide();if(tipNumber>0)addMessage('ari',tips[tipNumber]);});
$('askoGuideClose').addEventListener('click',closeGuide);
dialog.addEventListener('close',()=>{portrait.dataset.mood='happy';if(previousFocus?.isConnected)previousFocus.focus();});
dialog.addEventListener('click',event=>{if(event.target===dialog)closeGuide();});
form.addEventListener('submit',event=>{event.preventDefault();ask(input.value);input.value='';input.focus();});
document.querySelectorAll('[data-asko-question]').forEach(b=>b.addEventListener('click',()=>ask(b.dataset.askoQuestion)));
document.addEventListener('asko:report',event=>{
 report=event.detail;portrait.dataset.mood=report?'proud':'happy';
 if(dialog.open)addMessage('ari',report?'Nice! I can see '+report.counts.files+' local files, '+report.relationships.length+' import edges and '+report.counts.notes+' review notes. Ask me about them.':'The report was cleared. Ready for another scan.');
});
portrait.addEventListener('pointermove',event=>{
 const r=portrait.getBoundingClientRect(),x=Math.max(-1,Math.min(1,(event.clientX-r.left)/Math.max(1,r.width)*2-1)),y=Math.max(-1,Math.min(1,(event.clientY-r.top)/Math.max(1,r.height)*2-1));
 portrait.style.setProperty('--look-x',(x*3).toFixed(1)+'px');portrait.style.setProperty('--look-y',(y*2).toFixed(1)+'px');
});
portrait.addEventListener('pointerleave',()=>{portrait.style.setProperty('--look-x','0px');portrait.style.setProperty('--look-y','0px');});

