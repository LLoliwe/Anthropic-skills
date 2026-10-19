import { test } from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';

const __dirname=path.dirname(fileURLToPath(import.meta.url));
const html=readFileSync(path.join(__dirname,'..','educator-preview.html'),'utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
assert.ok(script,'private preview should contain first-party interaction code');

function boot(){
  const elements=new Map();
  for(const id of ['energy','water','temperature','steam','energyLabel','phase','audience','interest','inquiryPreview','copyStatus','emailInquiry','copyInquiry','path-title','path-answer']){
    elements.set(id,{value:id==='audience'?'Teacher preview':id==='interest'?'Water Lab':'0',textContent:'',style:{},handlers:{},addEventListener(type,fn){this.handlers[type]=fn;},dispatchEvent(ev){this.handlers[ev.type]?.(ev);}});
  }
  const stages=[0,1,2].map((i)=>({dataset:{node:String(i),energy:String([0,3344,25904][i])},pressed:i===0?'true':'false',handlers:{},addEventListener(type,fn){this.handlers[type]=fn;},setAttribute(name,value){if(name==='aria-pressed')this.pressed=value;}}));
  const branches=[0,1,2].map((i)=>({dataset:{node:String(i)},current:i===0,classList:{toggle(name,enabled){if(name==='is-current')this.owner.current=enabled;}}}));
  for(const branch of branches)branch.classList.owner=branch;
  const calls=[];
  const ctx={document:{getElementById(id){return elements.get(id)||null;},querySelectorAll(sel){return sel==='.path-stage'?stages:sel==='.path-art .branch'?branches:[];}},
    Event:class Event{constructor(type,opts){this.type=type;this.bubbles=Boolean(opts?.bubbles);}},
    window:{location:{href:''}},navigator:{clipboard:{async writeText(v){calls.push(v);}}},encodeURIComponent,Number,Math};
  vm.runInNewContext(script,ctx,{timeout:1200,filename:'LVL7 educator preview inline JS'});
  return {get:(id)=>elements.get(id),calls,ctx,stages,branches};
}

test('staged source remains an adult-only review with no hosted checkout, forms or child data',()=>{
  assert.match(html,/PRIVATE REVIEW • NOT FOR SALE YET/);
  assert.match(html,/a child-directed payment flow/i);
  assert.match(html,/mailto:partnerships@pryntor\.co\.za/);
  assert.doesNotMatch(html,/<(?:iframe|img)\b[^>]+src="https?:\/\//i);
  assert.doesNotMatch(html,/<script\s+[^>]*src=/i);
  assert.doesNotMatch(html,/(?:stripe\.com|paystack\.com|fetch\(|XMLHttpRequest|localStorage|document\.cookie)/i);
});

test('water model 0, 33.44 and 259.04 kJ uses correct temperature/phase math',()=>{
  assert.equal(100*4.18*80/1000,33.44);
  assert.ok(Math.abs(100*2256/1000+33.44-259.04)<1e-9);
  const {get}=boot();
  assert.equal(get('temperature').textContent,'20.0°C');
  assert.equal(get('energyLabel').textContent,'0.00 kJ');
  get('energy').value='3344';get('energy').handlers.input();
  assert.equal(get('temperature').textContent,'100.0°C');
  assert.equal(get('energyLabel').textContent,'33.44 kJ');
  assert.match(get('phase').textContent,/0% vapour/);
  get('energy').value='14624';get('energy').handlers.input();
  assert.equal(get('temperature').textContent,'100.0°C');
  assert.match(get('phase').textContent,/50% vapour/);
  get('energy').value='25904';get('energy').handlers.input();
  assert.equal(get('energyLabel').textContent,'259.04 kJ');
  assert.equal(get('water').style.height,'0.000%');
  assert.match(get('phase').textContent,/100% vapour/);
});

test('educator inquiry configuration is real and creates consent-based outbound draft only',async()=>{
  const {get,calls,ctx}=boot();
  get('audience').value='School pilot';get('audience').handlers.change();
  get('interest').value='Physics';get('interest').handlers.change();
  assert.match(get('inquiryPreview').textContent,/School pilot \/ Physics/);
  get('emailInquiry').handlers.click();
  assert.match(ctx.window.location.href,/^mailto:partnerships@pryntor\.co\.za\?/);
  assert.match(decodeURIComponent(ctx.window.location.href),/school pilot focused on Physics/);
  await get('copyInquiry').handlers.click();
  assert.match(calls[0],/written fee quote before any commitment/);
  assert.match(get('copyStatus').textContent,/Inquiry copied/);
});

test('interactive branching science path stays coupled to the real energy model, not a fake mastery badge',()=>{
  const {get,stages,branches}=boot();
  assert.equal(stages[0].pressed,'true');
  assert.equal(get('path-title').textContent,'Why does temperature rise first?');
  stages[1].handlers.click();
  assert.equal(get('energyLabel').textContent,'33.44 kJ');
  assert.equal(get('temperature').textContent,'100.0°C');
  assert.equal(stages[1].pressed,'true');
  assert.equal(branches[1].current,true);
  assert.match(get('path-answer').textContent,/latent heat/);
  stages[2].handlers.click();
  assert.equal(get('energyLabel').textContent,'259.04 kJ');
  assert.equal(get('water').style.height,'0.000%');
  assert.equal(branches[2].current,true);
  assert.match(get('path-answer').textContent,/225.6 kJ/);
  get('energy').value='15000';get('energy').handlers.input();
  assert.equal(stages[1].pressed,'true');
  assert.equal(stages[2].pressed,'false');
  assert.equal(branches[2].current,false);
  assert.match(html,/These are observations, not student mastery badges/);
});
