import test from 'node:test';import assert from 'node:assert/strict';import {transitionRoom,createCredential,workflowProgress} from '../src/domain.js';
test('checkout requires occupied room',()=>{assert.equal(transitionRoom({state:'occupied'},'check_out').state,'needs_attention');assert.throws(()=>transitionRoom({state:'ready'},'check_out'))});
test('credentials can cover multiple doors through rooms',()=>{const c=createCredential({guest_id:'g1',room_ids:['r1','r2','r1'],type:'pin',value:'4281',valid_from:'2026-01-01',valid_until:'2027-01-01'});assert.deepEqual(c.room_ids,['r1','r2'])});
test('workflow progress counts skipped as complete',()=>assert.equal(workflowProgress([{status:'done'},{status:'skipped'},{status:'open'}]),67));
