import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

const raw=readFileSync(new URL('../src/launchdesk-radar-r2.ts',import.meta.url),'utf8').trim();
const prefix='export const launchDeskHTML = ';
assert.ok(raw.startsWith(prefix)&&raw.endsWith(';'));
const html=JSON.parse(raw.slice(prefix.length,-1));
const route=readFileSync(new URL('../routes/index.ts',import.meta.url),'utf8');

test('Adobe Fonts uses authorized kit and a system fallback',()=>{
 assert.match(html,/https:\/\/use\.typekit\.net\/zss4psu\.css/);
 assert.match(html,/neue-haas-grotesk-display/);
 assert.match(html,/adobe-caslon-pro/);
 assert.match(html,/Helvetica Neue/);
 assert.match(html,/Adobe Fonts is loaded from Adobe.s CDN/);
 assert.match(route,/font-src https:\/\/use\.typekit\.net/);
 assert.match(route,/style-src 'unsafe-inline' https:\/\/use\.typekit\.net/);
 assert.doesNotMatch(route,/script-src [^;]*https:\/\/use\.typekit\.net/);
});

test('Motion is controlled, reduced-motion safe, and offline',()=>{
 assert.match(html,/id="motion-toggle"/);
 assert.match(html,/aria-label="Pause animation"/);
 assert.match(html,/prefers-reduced-motion: reduce/);
 assert.match(html,/html\.motion-off/);
 assert.match(html,/IntersectionObserver/);
 assert.match(html,/radar-sculpt/);
 assert.match(html,/max-width:420px/);
 assert.match(html,/\.mode \.online/);
 assert.match(html,/cancelAnimationFrame/);
 assert.match(html,/pointermove/);
 assert.doesNotMatch(html,/<video[^>]*autoplay|<audio[^>]*autoplay/i);
});

test('Core review actions remain present and locally scoped',()=>{
 for(const id of ['gate-nav','mark','next','previous','proof','project-name','sample','reset','export-top','export-bottom','api-label']){
   assert.ok(html.includes('id="'+id+'"'),'Missing control '+id);
 }
 assert.match(html,/localStorage\.setItem\(key/);
 assert.match(html,/independentApproval:false/);
 assert.match(html,/URL\.createObjectURL/);
 assert.match(html,/Browser-local/);
 assert.doesNotMatch(html,/https:\/\/www\.google-analytics\.com|googletagmanager\.com|segment\.com/i);
});
