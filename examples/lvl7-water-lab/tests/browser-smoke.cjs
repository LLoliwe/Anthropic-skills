const {chromium}=require('playwright');
const {readFile,mkdir}=require('node:fs/promises');
const path=require('node:path');
const assert=require('node:assert/strict');
(async()=>{
 const root=path.join(__dirname,'..');
 const html=await readFile(path.join(root,'index.html'),'utf8');
 const out=path.join(root,'screenshots');
 await mkdir(out,{recursive:true});
 const browser=await chromium.launch({headless:true});
 try{
  for(const v of [{name:'desktop',width:1440,height:940,motion:'no-preference'},{name:'phone',width:390,height:844,motion:'no-preference'},{name:'reduced',width:768,height:1024,motion:'reduce'}]){
   const page=await browser.newPage({viewport:{width:v.width,height:v.height},reducedMotion:v.motion});
   const errors=[];page.on('pageerror',error=>errors.push(String(error)));
   await page.setContent(html,{waitUntil:'load'});
   assert.equal(await page.locator('.topic').count(),6);
   assert.equal(await page.locator('#temp').textContent(),'20.0');
   await page.screenshot({path:path.join(out,v.name+'-original.png'),fullPage:true,animations:'disabled'});
   await page.locator('#boil').click();
   assert.equal(await page.locator('#temp').textContent(),'100.0');
   await page.locator('#energy').evaluate((el,value)=>{el.value=value;el.dispatchEvent(new Event('input',{bubbles:true}));},'147');
   assert.equal(await page.locator('#temp').textContent(),'100.0');
   assert.notEqual(await page.locator('#steam-pc').textContent(),'0%');
   await page.locator('#energy').evaluate((el,value)=>{el.value=value;el.dispatchEvent(new Event('input',{bubbles:true}));},'-41.76');
   assert.equal(await page.locator('#phase-label').textContent(),'Solid ice');
   await page.locator('#reset').click();
   assert.equal(await page.locator('#temp').textContent(),'20.0');
   await page.locator('#play').click();await page.waitForTimeout(230);
   assert(Number(await page.locator('#energy').inputValue())>0);
   await page.locator('#play').click();
   assert.equal(await page.locator('#play').getAttribute('aria-pressed'),'false');
   await page.locator('.topic[data-topic="states"]').click();
   assert.match(await page.locator('#path-summary').textContent(),/Tiny particles/);
   await page.locator('.reason-step[data-step="3"]').click();
   assert.match(await page.locator('#reason-feedback').textContent(),/first error/);
   await page.locator('.reason-step[data-step="2"]').click();
   assert.match(await page.locator('#reason-feedback').textContent(),/33\.44 kJ/);
   const sizes=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth}));
   assert(sizes.scroll<=sizes.client+1,'Unexpected horizontal overflow: '+JSON.stringify({view:v.name,sizes}));
   assert.equal(errors.length,0,'JS page errors: '+errors.join('; '));
   await page.screenshot({path:path.join(out,v.name+'-tested.png'),fullPage:true,animations:'disabled'});
   console.log('PASS original lab: '+v.name+', chemistry states, playback, graph, reasoning, no overflow or JS errors');
   await page.close();
  }
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
