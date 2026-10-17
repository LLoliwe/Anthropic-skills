// Asko V6: micro-interactions for the original vector Ari, cat, and actual local import graph.
// Runs without network or permanent storage. Animations respect reduced motion and visibility.
const $=id=>document.getElementById(id);
const cat=$('v6CatButton'),bubble=$('v6CatBubble'),wires=$('v5GraphWires');
const noMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
const tips=[
  'psst… tap a graph node!',
  'your code stays with you ♡',
  'want to explore? try a sample',
  'Ari can explain each scan ✳'
];
let tipIndex=0,resetCat=null;
cat.addEventListener('click',()=>{
  tipIndex=(tipIndex+1)%tips.length;
  bubble.textContent=tips[tipIndex];
  cat.classList.add('is-happy');
  if(resetCat!==null)clearTimeout(resetCat);
  resetCat=setTimeout(()=>{cat.classList.remove('is-happy');resetCat=null;},1700);
});
cat.addEventListener('pointerenter',()=>{if(!cat.classList.contains('is-happy'))bubble.textContent='tap for a tip ♡';});
function decorateConnections(){
  if(noMotion.matches||document.hidden)return;
  const paths=[...wires.querySelectorAll('path.v5-wire')];
  paths.forEach((path,index)=>{
    if(path.dataset.v6Animated==='true')return;
    path.dataset.v6Animated='true';
    const xmlns='http://www.w3.org/2000/svg';
    const orb=document.createElementNS(xmlns,'circle');
    orb.setAttribute('r','3.5');
    orb.setAttribute('class','v6-traveller');
    orb.setAttribute('data-v6-particle',String(index));
    // CSS offset-path keeps this animation stoppable by prefers-reduced-motion and screenshots.
    // Only actual measured relative-import connections produce moving particles.
    const d=path.getAttribute('d')||'';
    orb.style.offsetPath='path("'+d+'")';
    orb.style.offsetRotate='0deg';
    orb.style.animationDuration=(4.8+index*.7)+'s';
    orb.style.animationDelay=(-index*1.4)+'s';
    wires.append(orb);
  });
}
function updateGraphFocus(){
  const selected=$('v5GraphNodes')?.querySelector('[data-selected="true"]');
  for(const btn of $('v5GraphNodes')?.querySelectorAll('.v5-node')||[]){
    btn.setAttribute('aria-pressed',String(btn===selected));
  }
}
const observer=new MutationObserver(()=>{
  updateGraphFocus();
  if(!noMotion.matches)decorateConnections();
});
observer.observe($('v5GraphNodes'),{childList:true});
observer.observe(wires,{childList:true});
updateGraphFocus();decorateConnections();
noMotion.addEventListener('change',()=>{
  wires.querySelectorAll('[data-v6-particle]').forEach(x=>x.remove());
  wires.querySelectorAll('path.v5-wire').forEach(x=>delete x.dataset.v6Animated);
  if(!noMotion.matches)decorateConnections();
});
document.addEventListener('visibilitychange',()=>{
  if(document.hidden){
    wires.querySelectorAll('[data-v6-particle]').forEach(x=>x.remove());
    wires.querySelectorAll('path.v5-wire').forEach(x=>delete x.dataset.v6Animated);
  }else decorateConnections();
});

