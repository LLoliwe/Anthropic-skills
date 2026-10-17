// Real Chromium interaction and screenshot evidence. Requires playwright installed in CI.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { chromium } = require('playwright');
(async () => {
 const root = path.resolve(__dirname, '..');
 const types={'.html':'text/html','.css':'text/css','.mjs':'text/javascript'};
 const server=http.createServer((req,res)=>{
  const filename=path.join(root,decodeURI((req.url||'/').split('?')[0]==='/'?'/index.html':req.url).replace(/^\//,''));
  if(!filename.startsWith(root+path.sep)){res.writeHead(403);return res.end();}
  try {res.setHeader('Content-Type',types[path.extname(filename)]||'text/plain');res.end(fs.readFileSync(filename));}catch{res.writeHead(404);res.end('missing');}
 });
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  const out=path.join(root,'screenshots');fs.mkdirSync(out,{recursive:true});
  for(const [width,height,reduced] of [[1440,900,false],[390,844,true]]){
   const page=await browser.newPage({viewport:{width,height},reducedMotion:reduced?'reduce':'no-preference'});
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(`http://127.0.0.1:${server.address().port}/`,{waitUntil:'networkidle'});
   assert.equal(await page.locator('#force').textContent(),'9.81 N');
   assert.equal(await page.locator('#extension').textContent(),'24.53 mm');
   const before=await page.locator('#coils').getAttribute('d');
   await page.locator('#mass').focus();await page.keyboard.press('ArrowRight');
   assert.equal(await page.locator('#mass-label').textContent(),'1100 g');
   assert.equal(await page.locator('#force').textContent(),'10.79 N');
   assert.notEqual(await page.locator('#coils').getAttribute('d'),before);
   await page.locator('#step-minus').click();assert.equal(await page.locator('#mass-label').textContent(),'1000 g');
   await page.locator('#theme-toggle').click();assert.equal(await page.locator('html').getAttribute('data-theme'),'light');
   await page.locator('#reset').click();assert.equal(await page.locator('#mass-label').textContent(),'1000 g');
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
   if(reduced){await page.locator('#play-toggle').click();assert.equal(await page.locator('#play-toggle').getAttribute('aria-pressed'),'false');}
   assert.deepEqual(errors,[]);
   await page.screenshot({path:path.join(out,`lvl7-${width}.png`),fullPage:true});
   await page.close();
   console.log('CHROMIUM_PASS',width,reduced?'reduced-motion':'normal-motion');
  }
 } finally {await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1;});