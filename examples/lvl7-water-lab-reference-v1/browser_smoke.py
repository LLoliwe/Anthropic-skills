import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).parent
async def main():
 html=(ROOT/'index.html').read_text()
 results=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch()
  for width,height,reduced in [(1440,900,False),(390,844,False),(768,1024,True),(360,800,False)]:
   page=await browser.new_page(viewport={'width':width,'height':height},reduced_motion='reduce' if reduced else 'no-preference')
   errors=[];remote=[]
   page.on('pageerror',lambda x: errors.append(str(x)))
   page.on('request',lambda x: remote.append(x.url) if x.url.startswith(('http://','https://')) else None)
   await page.set_content(html,wait_until='load')
   assert await page.locator('#pip-boil').is_visible()
   await page.locator('#pip-boil').click()
   assert await page.locator('#temp').inner_text()=='100.0'
   assert 'flat line' in await page.locator('#pip-answer').inner_text()
   await page.locator('#pip-ask').click()
   await page.locator('#energy').evaluate('el=>{el.value="-41.76";el.dispatchEvent(new Event("input",{bubbles:true}))}')
   assert 'frozen' in await page.locator('#pip-answer').inner_text()
   await page.locator('#pip-path').click()
   assert 'six original' in await page.locator('#pip-answer').inner_text()
   assert await page.locator('.topic').count()==6
   await page.locator('.reason-step[data-step="2"]').click()
   assert '33.44' in await page.locator('#reason-feedback').inner_text()
   await page.locator('#reset').click()
   await page.locator('#pip-ask').click()
   assert await page.locator('#pip-phase').inner_text()=='LIQUID WATER'
   assert await page.locator('#temp').inner_text()=='20.0'
   sizes=await page.evaluate('({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth})')
   assert sizes['scroll']<=sizes['client']+1,(width,sizes)
   assert not errors,errors
   assert not remote,remote
   await page.screenshot(path=str(ROOT/(str(width)+'-verified.png')),full_page=True,animations='disabled')
   results.append({'width':width,'height':height,'reduced':reduced,'interactions':'PASS','pageErrors':len(errors),'externalRequests':len(remote),'overflow':False})
   await page.close()
  await browser.close()
 print(json.dumps(results,indent=2))
 (ROOT/'test-results.json').write_text(json.dumps(results,indent=2))
asyncio.run(main())
