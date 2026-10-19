import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const html=readFileSync(path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../educator-preview.html'),'utf8');
test('original R4 interactive study embeds 54 3D render views and works without third-party scripts',()=>{
 assert.equal((html.match(/data:image\/webp;base64,/g)||[]).length,54);
 assert.match(html,/THE WATER ROOM/);
 assert.match(html,/function frameState\(m\)/);
 assert.match(html,/window\.LVL7_R4_TEST=/);
 assert.doesNotMatch(html,/<script\b[^>]*\bsrc=/);
 assert.doesNotMatch(html,/<img\b[^>]*\bsrc\s*=\s*["']https?:/);
 assert.doesNotMatch(html,/(?:XMLHttpRequest|fetch\s*\(|localStorage|sessionStorage|document\.cookie|stripe\.com|paystack\.com)/i);
});
test('100 g heating and phase energy model is numerically correct, with transparent physical limits',()=>{
 assert.ok(Math.abs(100*4.18*80/1000-33.44)<1e-12);
 assert.ok(Math.abs(100*2256/1000-225.6)<1e-12);
 assert.ok(Math.abs(33.44+225.6-259.04)<1e-12);
 assert.match(html,/const WARM=33\.44,LATENT=225\.6,TOTAL=259\.04/);
 assert.match(html,/vap=k<=WARM\?0:Math\.min\(1,\(k-WARM\)\/LATENT\)/);
 assert.match(html,/vaporised completely at 100°C/);
 assert.match(html,/volumes are deliberately illustrative/i);
 assert.match(html,/not real-time WebGL/i);
 assert.match(html,/not computational fluid dynamics/i);
});
test('every meaningful 3D, model and educator interaction has actual controls',()=>{
 for(const pattern of [/id="energy"/,/data-state="0"/,/data-state="1"/,/data-state="2"/,/id="turnLeft"/,/id="turnRight"/,/pointermove/,/pointercancel/,/ArrowLeft/,/id="explainTitle"/,/id="explainText"/,/id="feedback"/,/id="copyInquiry"/,/id="audience"/,/id="interest"/]) assert.match(html,pattern);
});
test('review-only adult experiment respects website, child-safety and no-outreach freeze',()=>{
 assert.match(html,/PRIVATE ADULT REVIEW \/ NOT FOR SALE/);
 assert.match(html,/No children's details or student accounts/);
 assert.match(html,/not a scientifically certified curriculum lesson/i);
 assert.match(html,/not a live offer/i);
 assert.match(html,/sends nothing/i);
 assert.doesNotMatch(html,/<form\b/i);
 assert.doesNotMatch(html,/mailto:/i);
});
