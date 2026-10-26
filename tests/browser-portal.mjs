import {writeFileSync,readFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {connect} from './browser_client.mjs';
const b=await connect(process.env.COURSE_DEBUG_URL),base=process.env.COURSE_TEST_BASE;
const report={checks:[],axe:[],errors:[]};
const out='artifacts/platform';mkdirSync(out,{recursive:true});
function check(name,pass,details){report.checks.push({name,pass:!!pass,details});if(!pass)throw Error(name+': '+JSON.stringify(details));}
async function key(key,code,keyCode){await b.cdp('Input.dispatchKeyEvent',{type:'keyDown',key,code,text:key==='Enter'?'\r':undefined,windowsVirtualKeyCode:keyCode,nativeVirtualKeyCode:keyCode});await b.cdp('Input.dispatchKeyEvent',{type:'keyUp',key,code,text:key==='Enter'?'\r':undefined,windowsVirtualKeyCode:keyCode,nativeVirtualKeyCode:keyCode});}
async function go(route=''){await b.evaluate('window.__portalOldDocument=true');await b.cdp('Page.navigate',{url:new URL(route,base).href});await b.waitFor("!window.__portalOldDocument && document.readyState==='complete' && document.querySelector('.uso-skip-link')");}
try {
 const lock=JSON.parse(readFileSync('tests/browser-tools.json')).axe;
 const response=await fetch(lock.url);if(!response.ok)throw Error('axe download failed');const axe=await response.text();
 check('test-only axe integrity',createHash('sha256').update(axe).digest('hex')===lock.sha256);
 for(const [size,width,height,mobile] of [['desktop',1440,1100,false],['mobile',390,844,true]]){
  await b.cdp('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile});
  for(const route of ['','proyecto.html','licencias.html']) {
   await go(route);
   for(const mode of ['light','dark']) {
    await b.theme(mode);
    // Audit final rendered colors after Bootstrap navigation transitions finish.
    await new Promise(r=>setTimeout(r,300));
    check('no horizontal page overflow '+size+' '+route+' '+mode,await b.evaluate('document.documentElement.scrollWidth<=innerWidth+1'));
    await b.evaluate(axe);
    const result=await b.evaluate("axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}}).then(r=>({violations:r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))})),incomplete:r.incomplete.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)})),passes:r.passes.length}))");
    report.axe.push({size,route:route||'index.html',mode,...result});
    check('axe WCAG 2.2 AA '+size+' '+route+' '+mode,result.violations.length===0,result.violations);
    if(!route){
     const metrics=await b.cdp('Page.getLayoutMetrics');
     const png=await b.cdp('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:0,y:0,width:Math.ceil(metrics.cssContentSize.width),height:Math.ceil(metrics.cssContentSize.height),scale:1}});
     writeFileSync(`${out}/home-${size}-${mode}.png`,Buffer.from(png.data,'base64'));
    }
   }
  }
 }
 await b.cdp('Emulation.setDeviceMetricsOverride',{width:1440,height:1100,deviceScaleFactor:1,mobile:false});
 await go();
 await key('Tab','Tab',9);
 check('first Tab reaches skip link',await b.evaluate("document.activeElement.classList.contains('uso-skip-link')"));
 await key('Enter','Enter',13);
 check('skip link focuses main content',await b.evaluate("document.activeElement.id==='quarto-document-content'"));
 const names=[];
 // Start from the browser's document focus and traverse real tab stops.
 await go();
 for(let i=0;i<20;i++){
  await key('Tab','Tab',9);
  names.push(await b.evaluate("({tag:document.activeElement.tagName,cls:document.activeElement.className,href:document.activeElement.getAttribute('href'),label:document.activeElement.getAttribute('aria-label'),outline:getComputedStyle(document.activeElement).outlineStyle})"));
 }
 for(const slug of ['base-de-datos','inteligencia-artificial','precalculo'])check('course link reached by keyboard '+slug,names.some(n=>n.href===`https://ustudyopen.github.io/${slug}/`));
 check('theme toggle reached by keyboard',names.some(n=>String(n.cls).includes('quarto-color-scheme-toggle')));
 check('visible focus on interactive stops',names.filter(n=>n.tag==='A'||n.tag==='BUTTON').every(n=>n.outline!=='none'),names);
 await b.evaluate("document.querySelector('.quarto-color-scheme-toggle').focus()");
 const before=await b.evaluate("document.body.classList.contains('quarto-dark')");
 await key('Enter','Enter',13);
 await b.waitFor(`document.body.classList.contains('quarto-dark')!==${before}`);
 check('theme toggles with Enter',true);
 await b.cdp('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
 await go();
 await b.evaluate("document.querySelector('.navbar-toggler').focus()");
 await key('Enter','Enter',13);
 await b.waitFor("document.querySelector('.navbar-toggler').getAttribute('aria-expanded')==='true'");
 check('mobile menu expands with keyboard',true);
 await b.evaluate("[...document.querySelectorAll('.navbar-collapse a')].find(a=>a.getAttribute('href')?.includes('proyecto.html')).focus()");await key('Enter','Enter',13);
 await b.waitFor("location.pathname.endsWith('/proyecto.html') && document.readyState==='complete'");
 check('mobile navigation follows project link with keyboard',true);
 await b.cdp('Emulation.setDeviceMetricsOverride',{width:320,height:812,deviceScaleFactor:1,mobile:true});await go();
 check('320px reflow without horizontal scroll',await b.evaluate('document.documentElement.scrollWidth<=innerWidth+1'));
 check('no runtime or failed resources',b.errors.length===0,b.errors);
} catch(e){report.errors.push(e.stack||e.message);process.exitCode=1;} finally {
 b.close();writeFileSync(`${out}/portal-browser.json`,JSON.stringify(report,null,2));console.log(JSON.stringify({checks:report.checks.length,axeRuns:report.axe.length,failed:report.checks.filter(c=>!c.pass).length,errors:report.errors}));
}
