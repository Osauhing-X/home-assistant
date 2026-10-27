import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,readFile,writeFile,rm,unlink} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createRtspConnectClient} from '../src/lib/server/connect-client.js';
const secret=character=>character.repeat(43);
async function fixture(t){
 const root=await mkdtemp(join(tmpdir(),'rtsp-connect-'));t.after(()=>rm(root,{recursive:true,force:true}));
 let clock=1800000000000,response={device_code:secret('D'),user_code:'ABCD-1234',verification_uri:'https://iseteenindus.oux.ee/et/connect?user_code=ABCD-1234',expires_in:600,interval:5},status=200;const calls=[];
 const options={path:join(root,'connect.json'),now:()=>clock,fetcher:async(url,options)=>{calls.push({url,...options,body:JSON.parse(options.body)});return Response.json(response,{status});}};
 return {root,path:options.path,calls,client:createRtspConnectClient(options),restart:()=>createRtspConnectClient(options),advance:()=>clock+=5000,reply:(body,code=200)=>{response=body;status=code;}};
}
test('RTSP linking uses the fixed issuer, persistent identity and encrypted server-only credentials',async t=>{
 const f=await fixture(t),pending=await f.client.begin();assert.equal(pending.status,'awaiting_confirmation');
 assert.equal(f.calls[0].url,'https://iseteenindus.oux.ee/@_account/connect/begin');assert.equal(f.calls[0].body.service,'rtsp-to-onvif');assert.equal(f.calls[0].redirect,'error');
 assert.match(f.calls[0].body.installation_id,/^[A-Za-z0-9_-]{43}$/);assert.match(f.calls[0].body.challenge,/^[A-Za-z0-9_-]{43}$/);
 await f.restart().begin();assert.equal(f.calls.length,1,'pending flow survives restart without a duplicate');
 assert.doesNotMatch(await readFile(f.path,'utf8'),/ABCD-1234|DDDDDDDD/);await f.client.poll();assert.equal(f.calls.length,1,'poll interval is enforced');
 f.advance();f.reply({status:'connected',credential:secret('C'),installation:{id:secret('I'),service:'rtsp-to-onvif'},account:{email:'owner@example.invalid'}});
 const linked=await f.client.poll();assert.equal(linked.account_email,'owner@example.invalid');assert.equal(linked.status,'connected');assert.doesNotMatch(JSON.stringify(linked),/CCCCCCCC|device_code|verifier/);
 assert.doesNotMatch(await readFile(f.path,'utf8'),/CCCCCCCC|owner@example/);assert.equal(f.restart().view().installation_id,secret('I'));
 f.reply({status:'connected',installation:{id:secret('I'),service:'rtsp-to-onvif'},account:{email:'owner@example.invalid'}});await f.client.refresh();assert.equal(f.calls.at(-1).headers.authorization,'Bearer '+secret('C'));
 f.reply({error:'invalid_token'},401);assert.equal((await f.client.refresh()).status,'disconnected');
});
test('foreign confirmation URLs and wrong service responses never become links',async t=>{
 const f=await fixture(t);f.reply({device_code:secret('D'),user_code:'ABCD-1234',verification_uri:'https://attacker.invalid/et/connect?user_code=ABCD-1234',expires_in:600,interval:5});await assert.rejects(f.client.begin(),/invalid connection/);
 f.reply({device_code:secret('D'),user_code:'ABCD-1234',verification_uri:'https://iseteenindus.oux.ee/et/connect?user_code=ABCD-1234',expires_in:600,interval:5});await f.client.begin();f.advance();
 f.reply({status:'connected',credential:secret('C'),installation:{id:secret('I'),service:'workspace'},account:{email:'owner@example.invalid'}});await assert.rejects(f.client.poll(),/could not be verified/);assert.equal(f.client.view().status,'awaiting_confirmation');
});
test('corrupt state and a missing encryption key fail closed without replacing saved data',async t=>{
 const f=await fixture(t);await f.client.begin();const before=await readFile(f.path,'utf8');await unlink(join(f.root,'.connect-key'));
 assert.throws(()=>f.restart().view(),/could not be verified/);await assert.rejects(f.client.begin(),/could not be verified/);assert.equal(await readFile(f.path,'utf8'),before);
 await writeFile(f.path,'{broken');assert.throws(()=>f.restart().view(),/could not be read/);assert.equal(await readFile(f.path,'utf8'),'{broken');
});
