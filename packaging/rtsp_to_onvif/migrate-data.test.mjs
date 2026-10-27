import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,readFile,rm,readdir} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {migrateConfiguration} from './migrate-data.mjs';
import {assertMigrationComplete,MIGRATION_MARKER} from './migration-state.mjs';
async function fixture(t){const root=await mkdtemp(join(tmpdir(),'rtsp-migration-'));t.after(()=>rm(root,{recursive:true,force:true}));const source=join(root,'old'),target=join(root,'new');await mkdir(source);const cameras=JSON.stringify([{id:'front',username:'owner',password:'synthetic-private',hq:'rtsp://source/main'}]);await writeFile(join(source,'cameras.json'),cameras);return {root,source,target,cameras,sourceStopped:true};}
test('offline migration preserves source and private camera bytes, excluding derived relay config',async t=>{
 const f=await fixture(t);await writeFile(join(f.source,'mediamtx.yml'),'derived secret');const result=await migrateConfiguration(f);assert.equal(result.camera_count,1);assert.equal(result.source_retained,true);assert.equal(await readFile(join(f.target,'cameras.json'),'utf8'),f.cameras);assert.equal(await readFile(join(f.source,'cameras.json'),'utf8'),f.cameras);assert.deepEqual(await readdir(f.target),['cameras.json']);await assertMigrationComplete(f.target);
});
test('migration refuses missing stop acknowledgement and never overwrites existing targets',async t=>{
 const f=await fixture(t);await assert.rejects(migrateConfiguration({...f,sourceStopped:false}),/Stop the source/);await mkdir(f.target);await writeFile(join(f.target,'existing'),'preserve');await assert.rejects(migrateConfiguration(f),/never replaced/);assert.equal(await readFile(join(f.target,'existing'),'utf8'),'preserve');
});
test('incomplete account state, malformed cameras and colliding ports stop migration before target creation',async t=>{
 const f=await fixture(t);await writeFile(join(f.source,'connect.json'),'{}');await assert.rejects(migrateConfiguration(f),/both Connect/);await rm(join(f.source,'connect.json'));await writeFile(join(f.source,'settings.json'),JSON.stringify({onvifPort:8090}));await assert.rejects(migrateConfiguration(f),/must be different/);await rm(join(f.source,'settings.json'));await writeFile(join(f.source,'cameras.json'),'{broken');await assert.rejects(migrateConfiguration(f),/invalid/);assert.deepEqual(await readdir(f.root),['old']);
});
test('startup refuses a target marked as an incomplete migration',async t=>{
 const f=await fixture(t);await mkdir(f.target);await writeFile(join(f.target,MIGRATION_MARKER),'incomplete');await assert.rejects(assertMigrationComplete(f.target),/incomplete/);
});
