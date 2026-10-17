const {chromium}=require('playwright');const {readFileSync}=require('node:fs');const assert=require('node:assert/strict');const path=require('node:path');
(async()=>{
const html=readFileSync(path.join(__dirname,'..','index.html'),'utf8');
const browser=await chromium.launch({headless:true});
try{
for(const width of [320,390,430,1440]){
const page=await browser.newPage({viewport:{width,height:850},isMobile:width<500,hasTouch:width<500});
const errors=[];page.on('pageerror',e=>errors.push(String(e)));
await page.setContent(html,{waitUntil:'load'});
assert.equal(await page.locator('.engine-guard').isVisible(),false);
assert.equal(await page.locator('#engine-indicator').textContent(),'● LIQUID ENGINE RUNNING');
assert.equal(await page.locator('#temperature').textContent(),'20.0');
await page.locator('#stage-temp').evaluate(el=>{el.value='100';el.dispatchEvent(new Event('input',{bubbles:true}));});
await page.waitForTimeout(420);
assert.equal(await page.locator('#temperature').textContent(),'100.0');
assert((await page.evaluate('LVL7Fluid.state()')).emittedBubbles>0,'Water failed to boil');
if(width<500){await page.locator('#stage-steam').click();}else{await page.locator('#to-steam').click();}await page.waitForTimeout(350);
assert((await page.evaluate('LVL7Fluid.state()')).vapour>0,'Vapour failed to form');
assert((await page.evaluate('LVL7Fluid.state()')).emittedGas>0,'No steam emitted');
assert((await page.evaluate('LVL7Runtime.diagnostics()')).events>=2,'UI action not acknowledged');
const overflow=await page.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth');
assert(overflow<=1,'Mobile overflow '+width+': '+overflow);
assert.deepEqual(errors,[],'Client script exceptions '+width);
console.log('PASS live engine '+width+'px: true input, rising bubbles, vapour, status, no JS errors');
await page.close();
}
const disabled=await browser.newPage({viewport:{width:390,height:850},javaScriptEnabled:false,isMobile:true,hasTouch:true});
await disabled.setContent(html,{waitUntil:'load'});
assert.equal(await disabled.locator('.engine-guard').isVisible(),true);
await disabled.locator('#stage-temp').fill('100');
assert.equal(await disabled.locator('#temperature').textContent(),'20.0');
console.log('PASS JS-disabled QuickLook-style failure is visibly disclosed, not falsely animated');
await disabled.close();
}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});