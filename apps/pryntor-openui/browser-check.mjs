import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import { chromium } from 'playwright';
const root=path.resolve('dist');
const server=http.createServer(async(req,res)=>{try{const pathname=new URL(req.url,'http://localhost').pathname;const file=path.resolve(root,'.'+(pathname==='/'?'/index.html':pathname));if(!file.startsWith(root+path.sep))throw Error('path');const body=await fs.readFile(file);res.setHeader('Content-Type',file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':'text/html');res.end(body);}catch{res.writeHead(404).end();}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const url=`http://127.0.0.1:${server.address().port}`;
let browser;const checks=[];const errors=[];const external=[];
try{
 browser=await chromium.launch({headless:true,...(process.env.BROWSER_EXECUTABLE_PATH?{executablePath:process.env.BROWSER_EXECUTABLE_PATH,args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--disable-software-rasterizer','--no-zygote']}:{})});
 await fs.mkdir('evidence',{recursive:true});
 for(const width of [360,390,768,1440]){
  console.log('Checking width',width);const page=await browser.newPage({viewport:{width,height:1000}});page.setDefaultTimeout(8000);
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(!r.url().startsWith(url))external.push(r.url());});
  await page.goto(url);console.log('loaded');await page.getByText('5 demo items',{exact:true}).waitFor();
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`overflow ${width}`);
  console.log('filter');await page.getByRole('button',{name:'BTWW',exact:true}).click();await page.getByText('1 demo items',{exact:true}).waitFor();assert.equal(await page.locator('article').count(),1);
  await page.getByRole('button',{name:'LVL7',exact:true}).click();await page.getByRole('combobox',{name:'Work state',exact:true}).selectOption('Ready');await page.getByText('A clear lane.',{exact:true}).waitFor();
  await page.getByRole('button',{name:'All',exact:true}).click();await page.getByRole('combobox',{name:'Work state',exact:true}).selectOption('All');
  await page.getByText('Inspect the OpenUI payload',{exact:true}).click();await page.getByRole('button',{name:'Test invalid payload'}).click();await page.getByRole('alert').waitFor();assert.equal(await page.locator('article').count(),0);
  await page.getByRole('button',{name:'Restore valid demo'}).click();await page.getByText('5 demo items',{exact:true}).waitFor();
  await page.getByRole('button',{name:'BTWW',exact:true}).focus();await page.keyboard.press('Enter');await page.getByText('1 demo items',{exact:true}).waitFor();
  await page.getByRole('button',{name:'All',exact:true}).click();
  await page.screenshot({path:`evidence/openui-${width}.png`,fullPage:true});checks.push({width,overflow:false,filter:true,empty:true,invalidRejected:true,recovered:true,keyboard:true});await page.close();
 }
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 await fs.writeFile('evidence/browser.json',JSON.stringify({utc:new Date().toISOString(),checks,pageErrors:errors,externalRequests:external,humanReview:'PENDING'},null,2));console.log(JSON.stringify(checks));
}finally{if(browser)await browser.close();server.closeAllConnections();await new Promise(r=>server.close(r));}
