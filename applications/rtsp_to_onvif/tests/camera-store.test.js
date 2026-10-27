import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,readFile,rm,readdir,stat,mkdir} from 'node:fs/promises';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {createCameraStore} from '../src/lib/server/camera-store.js';
import {safeRelayLog} from '../src/lib/server/private-file.js';
async function fixture(t){const root=await mkdtemp(join(tmpdir(),'rtsp-store-'));t.after(()=>rm(root,{recursive:true,force:true}));return {root,store:createCameraStore(root)};}
test('only missing files use defaults; corrupt JSON and invalid structure are never overwritten',async t=>{
 const {root,store}=await fixture(t);assert.deepEqual(await store.cameras(),[]);assert.equal((await store.settings()).onvifPort,8091);
 for(const source of ['{invalid','{}','[null]']){await writeFile(join(root,'cameras.json'),source);await assert.rejects(store.cameras(),/invalid/);await assert.rejects(store.save([{id:'new'}]),/invalid/);assert.equal(await readFile(join(root,'cameras.json'),'utf8'),source);}
 await writeFile(join(root,'settings.json'),'[]');await assert.rejects(store.settings(),/invalid structure/);await assert.rejects(store.saveSettings({}),/invalid structure/);assert.equal(await readFile(join(root,'settings.json'),'utf8'),'[]');
});
test('filesystem errors are not treated as an empty configuration',async t=>{
 const {root,store}=await fixture(t);await mkdir(join(root,'cameras.json'));await assert.rejects(store.cameras(),/could not be read/);await assert.rejects(store.save([]),/could not be read/);
});
test('parallel read-modify-write operations retain every camera and recover after rejected callbacks',async t=>{
 const {root,store}=await fixture(t);await Promise.all(Array.from({length:20},(_,index)=>store.updateCameras(async all=>{await new Promise(resolve=>setImmediate(resolve));all.push({id:'camera-'+index,hq:'rtsp://synthetic/private'});})));assert.equal((await store.cameras()).length,20);
 await assert.rejects(store.updateCameras(all=>{all.length=0;throw Error('Synthetic rejection');}));assert.equal((await store.cameras()).length,20);
 await store.updateCameras(all=>{all[0].name='Changed';});assert.equal((await store.cameras())[0].name,'Changed');assert.equal((await readdir(root)).filter(name=>name.endsWith('.tmp')).length,0);
 if(process.platform!=='win32'){assert.equal((await stat(root)).mode&0o777,0o700);assert.equal((await stat(join(root,'cameras.json'))).mode&0o777,0o600);}
});
test('settings preserve approved defaults and bounds with durable replacement',async t=>{
 const {store}=await fixture(t);const saved=await store.saveSettings({onvifPort:9000,rtspPort:8555,discoveryPort:0,fragmentMs:1,gop:500});assert.equal(saved.onvifPort,9000);assert.equal(saved.fragmentMs,50);assert.equal(saved.gop,300);assert.deepEqual(await store.settings(),saved);
});
test('relay diagnostics redact URI-bearing messages, including multiline source values',()=>{
 assert.equal(safeRelayLog('relay started'),'relay started');
 for(const source of ['rtsp://synthetic:private@camera/stream','RTSPS://synthetic:private@camera/stream','rtsp://synthetic:private\nvalue@camera/stream'])assert.equal(safeRelayLog('upstream failed: '+source),'Stream event reported; RTSP source details redacted.');
});
