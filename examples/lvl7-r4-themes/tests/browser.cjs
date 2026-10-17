const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const {readFileSync,mkdirSync}=require('node:fs');
const path=require('node:path');
(async()=>{
const root=path.join(__dirname,'..'),html=readFileSync(path.join(root,'index.html'),'utf8');
const browser=await chromium.launch({headless:true});
try{
mkdirSync(path.join(root,'screenshots'),{recursive:true});
for(const [theme,width,height] of [['gallery',1440,900],['marine',1440,900],['signal',1440,900],['gallery',390,844],['marine',390,844],['signal',390,844],['gallery',768,1024]]){
const page=await browser.newPage({viewport:{width,height},reducedMotion:'reduce'}),errors=[];
page.on('pageerror',e=>errors.push(String(e)));
await page.setContent(html,{waitUntil:'load'});
await page.locator('[data-theme-btn="'+theme+'"]').click();
assert.equal(await page.locator('html').getAttribute('data-theme'),theme);
assert.equal(await page.locator('[data-theme-btn][aria-pressed="true"]').count(),1);
assert.equal(await page.locator('#particles .particle').count(),34);
assert.equal(await page.locator('#temperature').textContent(),'20.0');
await page.locator('#to-boil').click();assert.equal(await page.locator('#temperature').textContent(),'100.0');
await page.locator('#to-steam').click();assert.equal(await page.locator('#phase').textContent(),'Water vapour');
await page.locator('#to-ice').click();assert.equal(await page.locator('#phase').textContent(),'Ice');
await page.locator('#reset').click();assert.equal(await page.locator('#temperature').textContent(),'20.0');
await page.locator('#play').click();await page.waitForTimeout(200);
assert(Number(await page.locator('#energy').inputValue())>0);
await page.locator('#play').click();assert.equal(await page.locator('#play').getAttribute('aria-pressed'),'false');
await page.locator('[data-concept="boiling"]').click();assert.match(await page.locator('#concept-desc').textContent(),/To get here/);
await page.locator('[data-step="2"]').click();assert.match(await page.locator('#answer').textContent(),/33.44 kJ/);
const overflow=await page.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth');
assert(overflow<=1,'Overflow '+theme+'/'+width+'/'+overflow);
assert.deepEqual(errors,[]);
await page.locator('#reset').click();
await page.screenshot({path:path.join(root,'screenshots',theme+'-'+width+'.png'),fullPage:true,animations:'disabled'});
console.log('PASS '+theme+' '+width+' physical SVG/themes/logic/browser');
await page.close();
}
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});