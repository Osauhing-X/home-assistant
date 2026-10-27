import test from 'node:test';
import assert from 'node:assert/strict';
import {EventEmitter,once} from 'node:events';
import {PassThrough} from 'node:stream';
import {createServer} from 'node:http';
import {spawn} from 'node:child_process';
import {createHash} from 'node:crypto';
import {createSnapshotAuth} from '../src/lib/server/snapshot-auth.js';
import {createSnapshotHandler} from '../src/lib/server/snapshot.js';
import {hasGuiSession,token} from '../src/lib/server/gui-auth.js';
const camera={id:'synthetic',username:'onvif',password:'synthetic-password',hq:'rtsp://synthetic:private-value@127.0.0.1/stream'};
const event=(headers={},signal)=>{const url=new URL('http://127.0.0.1/snapshot/synthetic.jpg');return {params:{id:camera.id},url,request:new Request(url,{headers,signal}),cookies:{get:()=>undefined}};};
function worker(){const child=new EventEmitter();child.stdout=new PassThrough();child.stderr=new PassThrough();child.killed=false;child.kill=()=>{child.killed=true;return true;};return child;}
const jpeg=Buffer.from([255,216,255,217]);
test('missing GUI password never authenticates even with the former empty-password hash',()=>{
 const empty=createHash('sha256').update('rtsp-onvif:').digest('hex');assert.equal(token(''),null);assert.equal(hasGuiSession({get:()=>empty},''),false);
 assert.equal(hasGuiSession({get:()=>token('synthetic-gui')},'synthetic-gui'),true);
});
test('unauthenticated snapshot never launches FFmpeg or returns a frame',async()=>{
 let calls=0;const handle=createSnapshotHandler({cameras:async()=>[camera],spawn:()=>{calls++;return worker();}});
 const response=await handle(event());assert.equal(response.status,401);assert.match(response.headers.get('www-authenticate'),/^Digest /);assert.equal(calls,0);assert.equal(response.headers.get('cache-control'),'private, no-store');
});
test('real curl Digest client authenticates against the snapshot handler',async t=>{
 const handle=createSnapshotHandler({cameras:async()=>[camera],spawn:()=>{const child=worker();setImmediate(()=>{child.stdout.write(jpeg);child.emit('close',0);});return child;}});
 const server=createServer(async(req,res)=>{const result=await handle({params:{id:camera.id},url:new URL(req.url,'http://127.0.0.1:'+server.address().port),request:new Request('http://127.0.0.1:'+server.address().port+req.url,{headers:req.headers}),cookies:{get:()=>undefined}});res.writeHead(result.status,Object.fromEntries(result.headers));res.end(Buffer.from(await result.arrayBuffer()));});
 server.listen(0,'127.0.0.1');await once(server,'listening');t.after(()=>new Promise(resolve=>server.close(resolve)));
 const child=spawn(process.platform==='win32'?'curl.exe':'curl',['--silent','--show-error','--max-time','5','--digest','--user',camera.username+':'+camera.password,'http://127.0.0.1:'+server.address().port+'/snapshot/synthetic.jpg'],{windowsHide:true,stdio:['ignore','pipe','pipe']});
 const chunks=[];child.stdout.on('data',chunk=>chunks.push(chunk));child.stderr.resume();const [code]=await once(child,'exit');assert.equal(code,0);assert.deepEqual(Buffer.concat(chunks),jpeg);
});
test('Digest rejects replay, another URI, another camera, malformed headers and expired challenges',()=>{
 let clock=1800000000000;const auth=createSnapshotAuth({now:()=>clock});const nonce=auth.challenge(camera).match(/nonce="([^"]+)"/)[1];
 const uri='/snapshot/synthetic.jpg',cnonce='synthetic-client',nc='00000001',hash=value=>createHash('md5').update(value).digest('hex');
 const response=hash(hash(camera.username+':RTSP to ONVIF:'+camera.password)+':'+nonce+':'+nc+':'+cnonce+':auth:'+hash('GET:'+uri));
 const header=`Digest username="${camera.username}", realm="RTSP to ONVIF", nonce="${nonce}", uri="${uri}", response="${response}", qop=auth, nc=${nc}, cnonce="${cnonce}"`;
 const request=event({authorization:header});assert.equal(auth.authorized({...request,camera:{...camera,id:'another'}}),false);
 assert.equal(auth.authorized({...request,url:new URL('http://127.0.0.1/snapshot/other.jpg'),camera}),false);
 assert.equal(auth.authorized({...event({authorization:header+', nc=00000002'}),camera}),false);
 assert.equal(auth.authorized({...request,camera}),true);assert.equal(auth.authorized({...request,camera}),false);
 clock+=300001;assert.equal(auth.authorized({...request,camera}),false);
});
test('FFmpeg errors and non-JPEG output never expose upstream credentials',async()=>{
 const handle=createSnapshotHandler({cameras:async()=>[camera],auth:{authorized:()=>true},spawn:()=>{const child=worker();setImmediate(()=>{child.stderr.write(camera.hq);child.emit('close',1);});return child;}});
 const response=await handle(event());assert.equal(response.status,502);assert.equal(await response.text(),'Snapshot failed');
});
test('snapshot size, timeout, concurrent workers and request cancellation are bounded',async()=>{
 const workers=[];const handle=createSnapshotHandler({cameras:async()=>[camera],auth:{authorized:()=>true},timeoutMs:30,maxBytes:4,maxConcurrent:1,spawn:()=>{const child=worker();workers.push(child);return child;}});
 const first=handle(event());await new Promise(resolve=>setImmediate(resolve));assert.equal((await handle(event())).status,503);
 workers[0].stdout.write(Buffer.alloc(5));assert.equal((await first).status,502);assert.equal(workers[0].killed,true);
 assert.equal((await handle(event())).status,504);assert.equal(workers[1].killed,true);
 const controller=new AbortController(),pending=handle(event({},controller.signal));await new Promise(resolve=>setImmediate(resolve));controller.abort();assert.equal((await pending).status,408);assert.equal(workers[2].killed,true);
});
