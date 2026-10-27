import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {createOnvifAuthenticator} from '../src/lib/server/onvif-auth.js';
const camera={id:'front',username:'owner',password:'synthetic-private'};
const envelope=token=>`<s:Envelope><s:Header><wsse:Security><wsse:UsernameToken>${token}</wsse:UsernameToken></wsse:Security></s:Header><s:Body><GetUsers/></s:Body></s:Envelope>`;
function signed(clock,nonce='unique-one',patch={}){const created=new Date(clock).toISOString(),encoded=Buffer.from(nonce).toString('base64'),digest=createHash('sha1').update(Buffer.concat([Buffer.from(nonce),Buffer.from(created),Buffer.from(camera.password)])).digest('base64');return envelope(`<Username>${camera.username}</Username><Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">${digest}</Password><Nonce>${encoded}</Nonce><Created>${created}</Created>`).replace(patch.from||'__absent__',patch.to||'');}
test('valid digest is consumed once, including across cameras sharing credentials',()=>{
 const now=1800000000000,authenticate=createOnvifAuthenticator({now:()=>now}),xml=signed(now);
 assert.equal(authenticate(xml,camera,{consume:false}),true);assert.equal(authenticate(xml,camera,{consume:false}),true);assert.equal(authenticate(xml,camera),true);assert.equal(authenticate(xml,camera),false);assert.equal(authenticate(xml,{...camera,id:'other'}),false);assert.equal(authenticate(signed(now,'unique-two'),camera),true);
});
test('stale, future, malformed and partial digest tokens cannot authenticate',()=>{
 const now=1800000000000,authenticate=createOnvifAuthenticator({now:()=>now});
 for(const xml of [signed(now-300001),signed(now+60001),signed(now,'bad',{from:'<Nonce>',to:'<Missing>'}),signed(now,'bad',{from:'#PasswordDigest',to:'#Unknown'}),signed(now,'bad',{from:'<Created>',to:'<Missing>'}),signed(now,'bad',{from:'<Nonce>YmFk',to:'<Nonce>!!!'})])assert.equal(authenticate(xml,camera),false);
 assert.equal(authenticate(signed(now),{...camera,password:''}),false);
});
test('failed signatures do not consume nonces; a full cache rejects new tokens until expiry',()=>{
 let clock=1800000000000;const authenticate=createOnvifAuthenticator({now:()=>clock,maxNonces:1}),xml=signed(clock);
 assert.equal(authenticate(xml,{...camera,password:'wrong'}),false);assert.equal(authenticate(xml,camera),true);assert.equal(authenticate(signed(clock,'two'),camera),false);clock+=300002;assert.equal(authenticate(signed(clock,'new'),camera),true);
});
test('credentials must be in a single header token; empty legacy credentials and ambiguous fields are refused',()=>{
 const authenticate=createOnvifAuthenticator();
 const plain='<Username>owner</Username><Password>synthetic-private</Password>';
 assert.equal(authenticate(envelope(plain),camera),true);
 for(const xml of [`<s:Envelope><s:Body>${plain}</s:Body></s:Envelope>`,envelope(plain+plain),envelope(plain+'<Nonce>YQ==</Nonce><Nonce>Yg==</Nonce><Created>one</Created><Created>two</Created>'),envelope('<Username/><Password/>'),'<!DOCTYPE test>'+envelope(plain),'x'.repeat(65537)])assert.equal(authenticate(xml,camera),false);
 assert.equal(authenticate(null,camera),false);assert.equal(authenticate(envelope(plain),{username:'',password:''}),false);
 assert.equal(authenticate(envelope('<Username>owner</Username><Password>a&amp;b</Password>'),{...camera,password:'a&b'}),true);
});
