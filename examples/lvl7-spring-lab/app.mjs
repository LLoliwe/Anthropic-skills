import { calculate } from './model.mjs';

const input = document.querySelector('#mass');
const massLabel = document.querySelector('#mass-label');
const force = document.querySelector('#force');
const extension = document.querySelector('#extension');
const formula = document.querySelector('#formula');
const moving = document.querySelector('#moving-load');
const coils = document.querySelector('#coils');
const loadLabel = document.querySelector('#load-label');
const marker = document.querySelector('#ruler-marker');
const hint = document.querySelector('#live-hint');
const themeToggle = document.querySelector('#theme-toggle');
const playToggle = document.querySelector('#play-toggle');
const reset = document.querySelector('#reset');
const stepMinus = document.querySelector('#step-minus');
const stepPlus = document.querySelector('#step-plus');
let animating = false;
let lastFrame = 0;
let direction = 1;

function springPath(length) {
  const baseY = 150;
  const top = baseY + 15;
  const bottom = baseY + length - 14;
  const turns = 12;
  let d = `M 450 ${baseY} L 450 ${top}`;
  for (let i=0; i<=turns*2; i++) {
    const y = top + ((bottom-top)*i)/(turns*2);
    const x = i===0 || i===turns*2 ? 450 : 450 + (i%2 ? 18 : -18);
    d += ` L ${x.toFixed(1)} ${y.toFixed(1)}`;
  }
  return d+` L 450 ${baseY+length}`;
}
function display(massGrams) {
  const d = calculate(massGrams);
  const offsetPx = (d.extensionMm / 50) * 78;
  moving.setAttribute('transform',`translate(0 ${(offsetPx - 40).toFixed(3)})`);
  coils.setAttribute('d',springPath(72+offsetPx));
  marker.setAttribute('transform', `translate(0 ${offsetPx.toFixed(3)})`);
  massLabel.textContent = `${d.massGrams.toFixed(0)} g`;
  loadLabel.textContent = `${d.massGrams} g`;
  force.textContent = `${d.forceN.toFixed(2)} N`;
  extension.textContent = `${d.extensionMm.toFixed(2)} mm`;
  formula.textContent = `x = (${d.massKg.toFixed(2)} × 9.81) ÷ 400 = ${d.extensionM.toFixed(4)} m`;
  input.setAttribute('aria-valuetext', `${d.massGrams} grams, ${d.forceN.toFixed(2)} newtons, ${d.extensionMm.toFixed(2)} millimetres extension`);
  hint.textContent = `Load ${d.massGrams} grams produces ${d.forceN.toFixed(2)} newtons and ${d.extensionMm.toFixed(2)} millimetres extension`;
  return d;
}
const clamp = n => Math.max(0,Math.min(2000,Math.round(n/100)*100));
function setValue(n) { input.value = clamp(n); display(Number(input.value)); }
input.addEventListener('input',()=> { stop(); display(Number(input.value)); });
stepMinus.addEventListener('click',()=>{ stop();setValue(Number(input.value)-100);input.focus();});
stepPlus.addEventListener('click',()=>{ stop();setValue(Number(input.value)+100);input.focus();});
reset.addEventListener('click',()=>{ stop();setValue(1000);input.focus();});
function stop(){animating=false;playToggle.textContent='Play motion';playToggle.setAttribute('aria-pressed','false');}
function frame(ts){
  if(!animating)return;
  if (ts-lastFrame>100){
    const n=Number(input.value);
    if(n>=2000)direction=-1; else if(n<=0)direction=1;
    setValue(n+direction*100);lastFrame=ts;
  }
  requestAnimationFrame(frame);
}
playToggle.addEventListener('click',()=>{
  if(animating){stop();return;}
  if(window.matchMedia('(prefers-reduced-motion: reduce)').matches){
    hint.textContent='Automatic motion disabled because reduced motion is enabled. Use the slider or step buttons.';
    return;
  }
  animating=true;lastFrame=0;playToggle.textContent='Pause motion';playToggle.setAttribute('aria-pressed','true');requestAnimationFrame(frame);
});
themeToggle.addEventListener('click',()=>{
  const light=document.documentElement.dataset.theme!=='light';
  document.documentElement.dataset.theme=light?'light':'dark';
  themeToggle.textContent=light?'Dark mode':'Light mode';
  themeToggle.setAttribute('aria-label',light?'Switch to dark mode':'Switch to light mode');
});
display(Number(input.value));