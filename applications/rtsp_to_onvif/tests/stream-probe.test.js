import test from 'node:test';
import assert from 'node:assert/strict';
import {EventEmitter} from 'node:events';
import {PassThrough} from 'node:stream';
import {createStreamProbe} from '../src/lib/server/stream-probe.js';
function fixture(options={}){const children=[];const service=createStreamProbe({...options,spawnProcess:()=>{const child=Object.assign(new EventEmitter(),{pid:123,stdout:new PassThrough(),stderr:new PassThrough(),killed:false,kill(){this.killed=true;return true;}});children.push(child);return child;}});return {service,children};}
const uri='rtsp://synthetic:private@127.0.0.1/camera';
function complete(child){child.stdout.write(JSON.stringify({streams:[{codec_name:'h264',width:1920,height:1080,r_frame_rate:'25/1',secret:'must not leak'}]}));child.emit('close',0);}
test('same-source probes share a worker, saturation is bounded and responses are allow-listed',async()=>{
 const {service,children}=fixture({maxWorkers:1});const first=service.probe(uri),second=service.probe(uri);
 assert.equal(children.length,1);assert.match((await service.probe(uri+'2')).error,/busy/);
 complete(children[0]);assert.deepEqual(await first,await second);assert.equal((await service.probe(uri)).fps,25);assert.equal(children.length,1);assert.doesNotMatch(JSON.stringify(await first),/private|secret|must not leak/);service.stop();
});
test('timeout and oversized output kill workers, retaining capacity until actual close',async()=>{
 const a=fixture({maxWorkers:1,timeoutMs:5});const result=await a.service.probe(uri);assert.match(result.error,/timed out/);assert.equal(a.children[0].killed,true);assert.match((await a.service.probe(uri+'2')).error,/busy/);a.children[0].emit('close',1);a.service.stop();
 const b=fixture({maxBytes:8});const pending=b.service.probe(uri);b.children[0].stdout.write(Buffer.alloc(9));assert.match((await pending).error,/too large/);assert.equal(b.children[0].killed,true);b.children[0].emit('close',1);b.service.stop();
});
test('cache has bounded entries, expires and never returns mutable shared results',async()=>{
 let clock=0;const {service,children}=fixture({maxCache:1,ttlMs:5,now:()=>clock});const one=service.probe(uri);complete(children[0]);const value=await one;value.width=1;assert.equal((await service.probe(uri)).width,1920);
 const two=service.probe(uri+'2');complete(children[1]);await two;const three=service.probe(uri);assert.equal(children.length,3);complete(children[2]);await three;clock=5;const expired=service.probe(uri);assert.equal(children.length,4);complete(children[3]);await expired;
 for(const bad of ['https://host','rtsp://','rtsp://host\n/path'])assert.match((await service.probe(bad)).error,/Invalid/);service.stop();assert.match((await service.probe(uri)).error,/stopping/);
});
