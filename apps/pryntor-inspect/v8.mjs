// Asko V8: deterministic, browser-local emotional performance for original SVG Ari.
const $=id=>document.getElementById(id);
const hero=$('askoMascot'),card=$('v8CardMascot'),buttons=[...document.querySelectorAll('[data-v8-expression]')],status=$('v8ReactionStatus'),bubble=$('v8ExpressionBubble');
const scripts={
 laugh:{bubble:'HAHA! 😂',status:'Ari cracks up. You got her laughing!'},
 wink:{bubble:'gotcha 😉',status:'Ari gives you a cheeky wink.'},
 silly:{bubble:'blehhh 😛',status:'Ari pulls a ridiculous face.'},
 shock:{bubble:'WAIT—WHAT?! 😮',status:'Ari is dramatically surprised.'},
 proud:{bubble:'we did it! ✳',status:'Ari celebrates your on-device scan.'},
 happy:{bubble:'hey, you! ✳',status:''}
};
let timeout=null,pointTimer=0;
function setExpression(expression,reset=true){
 if(!Object.hasOwn(scripts,expression))return;
 if(timeout!==null){clearTimeout(timeout);timeout=null;}
 hero.dataset.expression=expression;card.dataset.expression=expression;
 bubble.textContent=scripts[expression].bubble;
 status.textContent=scripts[expression].status;
 buttons.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.v8Expression===expression)));
 if(reset&&expression!=='happy')timeout=setTimeout(()=>setExpression('happy',false),expression==='laugh'?3400:2700);
}
buttons.forEach(button=>button.addEventListener('click',()=>setExpression(button.dataset.v8Expression)));
hero.addEventListener('pointermove',event=>{
 if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;
 const now=performance.now();if(now-pointTimer<30)return;pointTimer=now;
 const b=hero.getBoundingClientRect(),x=Math.max(-1,Math.min(1,((event.clientX-b.left)/b.width-.5)*2)),y=Math.max(-1,Math.min(1,((event.clientY-b.top)/b.height-.5)*2));
 hero.style.setProperty('--look-x',(x*2.8).toFixed(1)+'px');
 hero.style.setProperty('--look-y',(y*2).toFixed(1)+'px');
});
hero.addEventListener('pointerleave',()=>{hero.style.setProperty('--look-x','0px');hero.style.setProperty('--look-y','0px');});
document.addEventListener('asko:report',event=>{if(event.detail)setExpression('proud');});
document.addEventListener('visibilitychange',()=>{if(document.hidden){setExpression('happy',false);}});
setExpression('happy',false);
