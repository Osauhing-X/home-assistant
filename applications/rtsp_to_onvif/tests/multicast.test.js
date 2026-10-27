import test from 'node:test';
import assert from 'node:assert/strict';
import {joinDiscoveryMulticast} from '../src/lib/server/multicast.js';
test('missing multicast interface does not escape the listening callback or kill management',()=>{
 let closed=0,unavailable=0;
 assert.equal(joinDiscoveryMulticast({addMembership(){throw Object.assign(Error('No interface'),{code:'ENODEV'});},close(){closed++;}},()=>unavailable++),false);
 assert.equal(closed,1);assert.equal(unavailable,1);
 assert.doesNotThrow(()=>joinDiscoveryMulticast({addMembership(){throw Error();},close(){throw Error();}}));
});
test('available multicast joins the ONVIF discovery group without marking it unavailable',()=>{
 let group;assert.equal(joinDiscoveryMulticast({addMembership(value){group=value;}},()=>assert.fail('must remain available')),true);assert.equal(group,'239.255.255.250');
});
