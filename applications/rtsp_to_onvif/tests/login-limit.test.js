import test from 'node:test';
import assert from 'node:assert/strict';
import {createLoginLimit} from '../src/lib/server/login-limit.js';
import {attemptGuiLogin} from '../src/lib/server/gui-login.js';
const request=password=>new Request('http://local/login',{method:'POST',body:new URLSearchParams({password,next:'/connect'})});
test('login failures enforce a temporary per-client block and recover after its expiry',()=>{
 let clock=0;const limit=createLoginLimit({now:()=>clock,maxFailures:2,blockMs:60000});assert.equal(limit.failure('one').allowed,true);assert.equal(limit.failure('one').allowed,false);assert.equal(limit.check('one').retry_after,60);assert.equal(limit.check('two').allowed,true);clock=60000;assert.equal(limit.check('one').allowed,true);assert.equal(limit.failure('one').allowed,true);limit.success('one');assert.equal(limit.failure('one').allowed,true);
});
test('global failure cap and bounded client records cannot be bypassed by rotating addresses',()=>{
 let clock=0;const limit=createLoginLimit({now:()=>clock,globalFailures:2});limit.failure('one');limit.failure('two');assert.equal(limit.check('three').allowed,false);clock=60000;assert.equal(limit.check('three').allowed,true);
 const bounded=createLoginLimit({now:()=>clock,maxClients:1,windowMs:1000});bounded.failure('one');assert.equal(bounded.check('two').allowed,false);clock+=1001;assert.equal(bounded.check('two').allowed,true);
});
test('both form encodings work without returning passwords and blocked requests cannot authenticate',async()=>{
 const limit=createLoginLimit({maxFailures:1});const denied=await attemptGuiLogin({request:request('wrong'),address:'one',password:'synthetic-correct',limit});assert.equal(denied.status,429);assert.equal((await attemptGuiLogin({request:request('synthetic-correct'),address:'one',password:'synthetic-correct',limit})).status,429);
 const form=new FormData();form.set('password','synthetic-correct');form.set('next','/connect');const accepted=await attemptGuiLogin({request:new Request('http://local/login',{method:'POST',body:form}),address:'two',password:'synthetic-correct',limit});assert.deepEqual(accepted,{ok:true,next:'/connect'});assert.doesNotMatch(JSON.stringify(denied),/wrong|synthetic-correct/);
 assert.equal((await attemptGuiLogin({request:request(''),address:'three',password:'',limit})).ok,false);
});
