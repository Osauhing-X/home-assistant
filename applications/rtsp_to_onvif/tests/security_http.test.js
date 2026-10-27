import test from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {createServer} from 'node:http';
import {mkdtemp,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {token} from '../src/lib/server/gui-auth.js';
test('built snapshot, management and login boundaries stay protected without starting hardware services',{timeout:20000},async()=>{
 const root=await mkdtemp(join(tmpdir(),'rtsp-http-')),probe=createServer();probe.listen(0,'127.0.0.1');await once(probe,'listening');const port=probe.address().port;await new Promise(resolve=>probe.close(resolve));
 const origin='http://127.0.0.1:'+port,password='synthetic-gui-only',camera={id:'synthetic',username:'onvif',password:'synthetic-onvif',hq:'rtsp://synthetic:private@127.0.0.1/stream'};
 await writeFile(join(root,'cameras.json'),JSON.stringify([camera]));
 const child=spawn(process.execPath,['build/index.js'],{cwd:fileURLToPath(new URL('../',import.meta.url)),windowsHide:true,stdio:'ignore',env:{PATH:process.env.PATH,SystemRoot:process.env.SystemRoot,TEMP:process.env.TEMP,TMP:process.env.TMP,NODE_ENV:'test',RTSP_ONVIF_OFFLINE_TEST:'true',RTSP_ONVIF_DATA:root,HOST:'127.0.0.1',PORT:String(port),ORIGIN:origin,PASSWORD:password}});
 const exited=once(child,'exit');
 try{
  let ready=false;for(let attempt=0;attempt<80;attempt++){try{if((await fetch(origin+'/login')).ok){ready=true;break;}}catch{}await new Promise(resolve=>setTimeout(resolve,100));}assert.equal(ready,true,'build the application before running HTTP tests');
  const snapshot=await fetch(origin+'/snapshot/synthetic.jpg');assert.equal(snapshot.status,401);assert.match(snapshot.headers.get('www-authenticate'),/^Digest /);assert.doesNotMatch(await snapshot.text(),/private|rtsp:\/\//);
  const denied=await fetch(origin+'/api/cameras',{redirect:'manual'});assert.equal(denied.status,401);assert.deepEqual(await denied.json(),{error:'Authentication required'});
  const cookie='rtsp_onvif_auth='+token(password);assert.equal((await fetch(origin+'/api/cameras',{headers:{cookie}})).status,200);
  const cross=await fetch(origin+'/api/cameras',{method:'POST',headers:{cookie,origin:'https://attacker.test','content-type':'application/json'},body:'{}'});assert.equal(cross.status,403);
  const incomplete=await fetch(origin+'/api/cameras',{method:'POST',headers:{cookie,origin,'content-type':'application/json'},body:JSON.stringify({id:'new',hq:'rtsp://127.0.0.1/other',password:''})});assert.equal(incomplete.status,409,'camera credentials cannot be empty');
  const login=await fetch(origin+'/login/session',{method:'POST',headers:{origin,'content-type':'application/x-www-form-urlencoded'},body:new URLSearchParams({password,next:'/\\attacker.test/'}),redirect:'manual'});assert.equal(login.status,303);assert.equal(login.headers.get('location'),'/');assert.match(login.headers.get('set-cookie'),/HttpOnly/i);
  const soap='<s:Envelope><s:Header><Username>onvif</Username><Password>synthetic-onvif</Password></s:Header><s:Body><GetSnapshotUri/></s:Body></s:Envelope>';
  for(const path of ['/onvif/synthetic/media_service','/onvif/media_service']){const response=await fetch(origin+path,{method:'POST',headers:{'content-type':'application/soap+xml'},body:soap});assert.equal(response.status,200);const xml=await response.text();assert.match(xml,/<tt:Timeout>PT0S<\/tt:Timeout>/);assert.match(xml,/\/snapshot\/synthetic\.jpg/);assert.doesNotMatch(xml,/synthetic-onvif|private@/);}
  for(const path of ['/onvif/synthetic/media_service','/onvif/media_service']){const response=await fetch(origin+path,{method:'POST',headers:{'content-type':'application/soap+xml'},body:soap.replace('GetSnapshotUri','GetStreamUri')});assert.equal(response.status,200);const xml=await response.text();assert.match(xml,/rtsp:\/\/127\.0\.0\.1:8554\/synthetic/);assert.doesNotMatch(xml,/private@|synthetic-onvif/);}
  assert.equal((await fetch(origin+'//attacker.test/',{redirect:'manual'})).status,400);
 }finally{child.kill();await exited;await rm(root,{recursive:true,force:true});}
});
