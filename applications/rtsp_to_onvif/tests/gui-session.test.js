import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {token,hasGuiSession,SESSION_SECONDS} from '../src/lib/server/gui-auth.js';
const cookies=value=>({get:()=>value});
test('GUI sessions have random identity and server-enforced expiry',()=>{
 const now=1800000000000,a=token('synthetic-password',now),b=token('synthetic-password',now);
 assert.notEqual(a,b);assert.equal(hasGuiSession(cookies(a),'synthetic-password',now),true);
 assert.equal(hasGuiSession(cookies(a),'synthetic-password',now+SESSION_SECONDS*1000-1),true);
 assert.equal(hasGuiSession(cookies(a),'synthetic-password',now+SESSION_SECONDS*1000),false);
 assert.equal(hasGuiSession(cookies(a),'synthetic-password',now-1000),false);
});
test('password rotation, tampering, missing settings and old static hashes cannot authenticate',()=>{
 const a=token('synthetic-password');
 for(const value of [undefined,'invalid',a.replace('v1.','v2.'),a.slice(0,-1)+'!',createHash('sha256').update('rtsp-onvif:synthetic-password').digest('hex')])assert.equal(hasGuiSession(cookies(value),'synthetic-password'),false);
 assert.equal(hasGuiSession(cookies(a),'different-password'),false);
 assert.equal(hasGuiSession(cookies(a),''),false);assert.equal(token(''),null);
});
