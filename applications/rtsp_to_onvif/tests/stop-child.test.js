import test from 'node:test';
import assert from 'node:assert/strict';
import {EventEmitter} from 'node:events';
import {stopChild} from '../src/lib/server/stop-child.js';
function child(){return Object.assign(new EventEmitter(),{pid:123,exitCode:null,signalCode:null,signals:[],kill(signal){this.signals.push(signal);return true;}});}
test('graceful child exit cancels forced shutdown and removes listeners',async()=>{
 const process=child(),stopped=stopChild(process,{graceMs:30});process.emit('close');await stopped;await new Promise(resolve=>setTimeout(resolve,40));assert.deepEqual(process.signals,['SIGTERM']);assert.equal(process.listenerCount('close'),0);
});
test('unresponsive media process is killed after its grace period and cannot block shutdown indefinitely',async()=>{
 const process=child();await stopChild(process,{graceMs:5,killWaitMs:5});assert.deepEqual(process.signals,['SIGTERM','SIGKILL']);assert.equal(process.listenerCount('close'),0);
});
test('failed spawns and already exited processes are not signalled',async()=>{
 const process=child();process.pid=undefined;await stopChild(process);assert.deepEqual(process.signals,[]);process.pid=123;process.exitCode=0;await stopChild(process);assert.deepEqual(process.signals,[]);
});
