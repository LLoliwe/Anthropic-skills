const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const http=require('node:http');
const path=require('node:path');
const root=path.resolve(__dirname,'../../..');
const prefix='/apps/lvl7-water-game-v1-1/';
(async()=>{
const server=http.createServer((req,res)=>{const file=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return;}try{res.setHeader('Content-Type',file.endsWith('.mjs')?'text/javascript':file.endsWith('.css')?'text/css':'text/html');res.end(fs.readFileSync(file));}catch{res.writeHead(404);res.end();}});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
let browser;
try{
browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH,args:['--no-sandbox']}: {})});
for(const width of [320,390,768,1440]){
 const page=await browser.newPage({viewport:{width,height:900},hasTouch:width<450,reducedMotion:'reduce'});const errors=[];const external=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(!r.url().startsWith('http://127.0.0.1'))external.push(r.url());});
 await page.goto(`http://127.0.0.1:${server.address().port}${prefix}curriculum.html`);
 assert.match(await page.locator('#result-count').textContent(),/6 concepts/);assert.deepEqual(external,[],'No external requests before opt-in');
 await page.locator('#search').fill('boiling');assert.equal(await page.locator('.concept-card').count(),1);await page.locator('.concept-card').click();assert.equal(await page.locator('#detail-title').textContent(),'Boiling water');
 await page.locator('#age').selectOption('4');assert(await page.locator('#empty').isVisible());await page.locator('#reset').click();assert.equal(await page.locator('.concept-card').count(),6);
 await page.locator('#soft').uncheck();assert(await page.locator('#path button').count()>0);
 assert(await page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'));
 if(process.env.MARBLE_SOURCE_DIR){
   await page.route('https://raw.githubusercontent.com/withmarbleapp/os-taxonomy/**',route=>route.fulfill({contentType:'application/json',body:fs.readFileSync(path.join(process.env.MARBLE_SOURCE_DIR,path.basename(route.request().url())))}));
   await page.locator('#load').click();await page.waitForFunction(()=>document.querySelector('#count').textContent.includes('1,590'));
   assert.match(await page.locator('#detail-title').textContent(),/Heating & Cooling/);assert.equal(await page.locator('#subject option').count(),9);
   await page.locator('#search').fill('fractions');await page.locator('#subject').selectOption('Mathematics');assert(await page.locator('.concept-card').count()>0);await page.locator('.concept-card').first().click();assert.equal(await page.locator('.lab-cta').count(),0);assert.match(await page.locator('#lab-link').textContent(),/not available/);
   await page.locator('#reset').click();await page.locator('#search').fill('Heating & Cooling');await page.locator('.concept-card').click();assert.equal(await page.locator('.lab-cta').count(),1);assert.match(await page.locator('#credit').textContent(),/Generative Spark/);
 }
 if(process.env.SCREENSHOT_DIR){fs.mkdirSync(process.env.SCREENSHOT_DIR,{recursive:true});await page.screenshot({path:path.join(process.env.SCREENSHOT_DIR,`atlas-${width}.png`),fullPage:true});}
 await page.locator('.lab-cta').click();await page.waitForFunction(()=>window.LVL7Runtime?.ready);assert.equal(await page.locator('#xp').textContent(),'0 XP');await page.locator('#btn-boil').click();assert.equal(await page.locator('#temperature').textContent(),'100.0');assert.equal(await page.locator('#xp').textContent(),'50 XP');
 assert.deepEqual(errors,[]);console.log(`PASS ${width}px: map, filters, empty/reset, pathway, lab navigation, boiling and XP${process.env.MARBLE_SOURCE_DIR?', checksum-verified full graph (local transport fixture)':''}`);await page.close();
}
const fail=await browser.newPage();await fail.route('https://raw.githubusercontent.com/**',r=>r.fulfill({contentType:'application/json',body:'{}'}));await fail.goto(`http://127.0.0.1:${server.address().port}${prefix}curriculum.html`);await fail.locator('#load').click();await fail.waitForFunction(()=>document.querySelector('#load-status').textContent.includes('checksum mismatch'));assert.equal(await fail.locator('.concept-card').count(),6);assert.equal(await fail.locator('#load').isEnabled(),true);console.log('PASS corrupted source fails closed, starter retained, retry available');await fail.close();
}finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error(e);process.exitCode=1;});
