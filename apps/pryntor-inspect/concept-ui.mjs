// Wires the reference-faithful marketing controls to actual on-device analysis.
const $=id=>document.getElementById(id);
const sampleLabels={web:'Original web-app demo',mobile:'Original mobile-ui demo',marketing:'Original marketing-site demo'};
document.querySelectorAll('[data-concept-sample]').forEach(button=>button.addEventListener('click',()=>{
 const name=button.dataset.conceptSample;
 if(!Object.hasOwn(sampleLabels,name))return;
 document.dispatchEvent(new CustomEvent('asko:load-concept-sample',{detail:name}));
}));
$('sidebarAgents').addEventListener('click',()=>$('askoGuideFab').click());
document.addEventListener('asko:report',event=>{
 const chosen=event.detail?.mode==='sample';
 document.querySelectorAll('[data-concept-sample]').forEach(button=>button.classList.toggle('concept-sample-active',chosen&&event.detail?.sampleId===button.dataset.conceptSample));
});
const artwork=$('askoMascot');
artwork?.addEventListener('pointermove',event=>{
 if(window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;
 const rect=artwork.getBoundingClientRect(),x=(event.clientX-rect.left)/rect.width-.5,y=(event.clientY-rect.top)/rect.height-.5;
 artwork.style.setProperty('--tilt-x',Math.max(-4,Math.min(4,-y*7)).toFixed(1)+'deg');
 artwork.style.setProperty('--tilt-y',Math.max(-4,Math.min(4,x*7)).toFixed(1)+'deg');
});
artwork?.addEventListener('pointerleave',()=>{
 artwork.style.setProperty('--tilt-x','0deg');artwork.style.setProperty('--tilt-y','0deg');
});
document.querySelectorAll('.concept-sidebar a').forEach(link=>link.addEventListener('click',()=>{
 document.querySelectorAll('.concept-sidebar a').forEach(other=>other.classList.remove('active'));link.classList.add('active');
}));

