import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const file=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../educator-preview.html');
const html=readFileSync(file,'utf8');

test('adult-only original LVL7 experiment stays private, no live sales or learner capture',()=>{
 assert.match(html,/PRIVATE R3 EXPERIMENT/);
 assert.match(html,/No student accounts or child data/);
 assert.match(html,/not a certified lesson/i);
 assert.match(html,/PRYNTOR.*PRIVATE SOURCE DESIGN/i);
 assert.match(html,/mailto:partnerships@pryntor\.co\.za\?subject=/);
 assert.doesNotMatch(html,/<(?:iframe|img|script)\b[^>]*\bsrc\s*=['"]https?:/i);
 assert.doesNotMatch(html,/(?:fetch\s*\(|XMLHttpRequest|localStorage|sessionStorage|document\.cookie|paystack|stripe\.com)/i);
});
test('physics uses transparent original 100 g idealised water model',()=>{
 assert.equal(100*4.18*80/1000,33.44);
 assert.equal(100*2256/1000,225.6);
 assert.ok(Math.abs(33.44+225.6-259.04)<1e-9);
 assert.match(html,/WARM_KJ=33\.44,LATENT_KJ=225\.6,TOTAL_KJ=259\.04/);
 assert.match(html,/no heat loss/i);
 assert.match(html,/not computational fluid dynamics/i);
 assert.match(html,/not validated CFD/i);
});
test('actual energy-linked canvas, 3 states, motion and accessible controls are wired',()=>{
 for(const pattern of [/id="labCanvas"/,/getContext\('2d'\)/,/getContext\('webgl2'/,/function drawFallback\(\)/,/function thermodynamic\(kJ\)/,/id="motionToggle"/,/prefers-reduced-motion: reduce/,/data-state="0"/,/data-state="1"/,/data-state="2"/,/pointercancel/,/ArrowLeft/,/aria-live="polite"/])assert.match(html,pattern);
});
test('educator inquiry optional and user-initiated, not an automatic sales funnel',()=>{
 for(const pattern of [/id="audience"/,/id="interest"/,/id="inquiryPreview"/,/id="emailInquiry"/,/id="copyInquiry"/,/window\.location\.href='mailto:partnerships@pryntor\.co\.za/])assert.match(html,pattern);
 assert.doesNotMatch(html,/<form\b/i);
});
