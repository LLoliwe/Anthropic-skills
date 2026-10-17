const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const {readFileSync,mkdirSync}=require('node:fs');
const path=require('node:path');
(async()=>{
const root=path.join(__dirname,'..');
const html=readFileSync(path.join(root,'index.html'),'utf8');
const browser=await chromium.launch({headless:true});
try{
mkdirSync(path.join(root,'screenshots'),{recursive:true});
for(const [width,height] of [[320,720],[390,844],[430,932],[768,1024],[1440,900]]){
 const page=await browser.newPage({viewport:{width,height},isMobile:width<=430,hasTouch:width<=430,reducedMotion:'reduce'});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.setContent(html,{waitUntil:'load'});
 assert.equal(await page.locator('#engine-guard').isVisible(),false);
 assert.equal(await page.locator('#xp').textContent(),'0 XP');
 assert(await page.evaluate('!!window.LVL7Fluid && !!window.LVL7Runtime?.ready'));
 const widthOverflow=await page.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth');
 assert(widthOverflow<=1,'Horizontal overflow '+width+': '+widthOverflow);
 await page.locator('#stage-temp').evaluate(el=>{el.value='100';el.dispatchEvent(new Event('input',{bubbles:true}));});
 await page.waitForTimeout(400);
 assert.equal(await page.locator('#temperature').textContent(),'100.0');
 assert.equal(await page.locator('#xp').textContent(),'50 XP');
 assert((await page.evaluate('LVL7Fluid.state()')).emittedBubbles>0);
 assert(await page.locator('[data-badge="boil"]').evaluate(el=>el.classList.contains('unlocked')));
 await page.locator('#stage-steam').click();await page.waitForTimeout(550);
 assert((await page.evaluate('LVL7Fluid.state()')).vapour>0);
 assert((await page.evaluate('LVL7Fluid.state()')).emittedGas>0);
 assert.equal(await page.locator('#stage-steam strong').textContent(),'Pause gas');
 await page.locator('#stage-steam').click();
 await page.evaluate('setEnergy(physics.boil+(physics.steam-physics.boil)*.35)');
 assert.equal(await page.locator('#xp').textContent(),'120 XP');
 assert(await page.locator('[data-badge="gas"]').evaluate(el=>el.classList.contains('unlocked')));
 await page.evaluate('setEnergy(physics.steam)');
 assert.equal(await page.locator('#xp').textContent(),'220 XP');
 assert.equal(await page.locator('#mission-name').textContent(),'All missions complete!');
 await page.locator('[data-step="2"]').click();
 assert.match(await page.locator('#reason-feedback').textContent(),/33.44 kJ/);
 await page.locator('#profile').click();
 assert.equal(await page.locator('#drawer').isVisible(),true);
 await page.locator('#reset-progress').click();
 assert.equal(await page.locator('#xp').textContent(),'0 XP');
 assert.equal(await page.locator('#temperature').textContent(),'20.0');
 await page.evaluate('window.LVL7Fluid.kick(65,0)');
 await page.waitForTimeout(100);
 assert((await page.evaluate('LVL7Fluid.state()')).disturbance>0);
 assert.deepEqual(errors,[]);
 await page.screenshot({path:path.join(root,'screenshots','gamified-'+width+'.png'),fullPage:true,animations:'disabled'});
 console.log('PASS '+width+'px — physics, rising gas, XP 50/120/220, achievements, reset, slosh, first mistake, no errors');
 await page.close();
}
const disabled=await browser.newPage({javaScriptEnabled:false,viewport:{width:390,height:844}});
await disabled.setContent(html,{waitUntil:'load'});
assert(await disabled.locator('#engine-guard').isVisible());
console.log('PASS native file-viewer no-JavaScript fallback');
await disabled.close();
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});