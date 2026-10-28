import test from 'node:test';
import assert from 'node:assert/strict';
import {EventEmitter} from 'node:events';
import {PassThrough} from 'node:stream';
import {createPreviewService} from '../src/lib/server/preview-service.js';
const uri='rtsp://synthetic:private@127.0.0.1/source';
function fixture(options={}){const children=[];const service=createPreviewService({...options,spawnProcess:()=>{const child=Object.assign(new EventEmitter(),{pid:123,exitCode:null,stdout:new PassThrough(),stderr:new PassThrough(),killed:false,kill(){this.killed=true;queueMicrotask(()=>{this.exitCode=0;this.emit('close',0);});return true;}});children.push(child);return child;}});return {service,children};}
test('preview tokens are bounded, expire and can only be consumed once',()=>{
 let clock=0;const {service}=fixture({maxTokens:1,now:()=>clock});const token=service.mint(uri);assert.throws(()=>service.mint(uri),error=>error.status===429);assert.equal(service.consume(token),uri);assert.equal(service.consume(token),'');const expired=service.mint(uri);clock=60000;assert.equal(service.consume(expired),'');assert.doesNotThrow(()=>service.mint(uri));for(const value of ['rtsp://','http://host','rtsp://host\n/path'])assert.throws(()=>service.mint(value),error=>error.status===400);
});
test('worker saturation never spawns another process and cancellation releases the slot after closure',async()=>{
 const {service,children}=fixture({maxWorkers:1});const response=service.open(uri,{});assert.equal(service.open(uri,{}).status,503);assert.equal(children.length,1);assert.throws(()=>service.mint(uri),error=>error.status===503);await response.body.cancel();assert.equal(children[0].killed,true);await new Promise(resolve=>setImmediate(resolve));const next=service.open(uri,{});assert.equal(next.status,200);await next.body.cancel();await service.stop();
});
test('slow readers apply backpressure and aborts never expose source credentials',async()=>{
 const {service,children}=fixture({queueBytes:4});const abort=new AbortController(),response=service.open(uri,{},abort.signal),child=children[0];child.stdout.write(Buffer.alloc(8));assert.equal(child.stdout.isPaused(),true);const reader=response.body.getReader();assert.equal((await reader.read()).value.byteLength,8);abort.abort();await assert.rejects(reader.read(),error=>!error.message.includes('private'));assert.equal(child.killed,true);await service.stop();
});
test('startup and maximum-duration timeouts stop workers and end streams',async()=>{
 const a=fixture({startupMs:5,durationMs:100});const response=a.service.open(uri,{});await assert.rejects(response.arrayBuffer(),/preview stopped/);assert.equal(a.children[0].killed,true);await a.service.stop();
 const b=fixture({startupMs:100,durationMs:5});const timed=b.service.open(uri,{});b.children[0].stdout.write(Buffer.from('synthetic'));assert.equal(Buffer.from(await timed.arrayBuffer()).toString(),'synthetic');assert.equal(b.children[0].killed,true);await b.service.stop();
});
