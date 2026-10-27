import test from 'node:test';
import assert from 'node:assert/strict';
import {readSoapBody} from '../src/lib/server/soap-body.js';
test('SOAP stream reading enforces the limit without destroying the connection before a 413 response',async()=>{
 let cancelled=false;
 const stream=new ReadableStream({start(controller){controller.enqueue(Buffer.alloc(4));controller.enqueue(Buffer.alloc(4));controller.enqueue(Buffer.alloc(4));},cancel(){cancelled=true;}});
 await assert.rejects(readSoapBody({body:stream},8),/limit/);assert.equal(cancelled,false);await stream.cancel();
 assert.equal((await readSoapBody(new Request('http://local',{method:'POST',body:'<xml/>'}))).toString(),'<xml/>');
});
