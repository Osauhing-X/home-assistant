import test from 'node:test';
import assert from 'node:assert/strict';
import net from 'node:net';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {mkdtemp,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {relayConfig} from '../src/lib/server/relay-config.js';

const binary=process.env.MEDIAMTX_TEST_BINARY;
test('MediaMTX enforces generated camera credentials and exact read permissions', {skip:!binary,timeout:20000}, async () => {
  const root=await mkdtemp(join(tmpdir(),'relay-auth-'));
  const probe=net.createServer();probe.listen(0,'127.0.0.1');await once(probe,'listening');const port=probe.address().port;await new Promise(resolve=>probe.close(resolve));
  const config=JSON.parse(relayConfig([{id:'alpha',username:'alice',password:'alpha-secret',hq:'rtsp://127.0.0.1/source',lq:'rtsp://127.0.0.1/low'},{id:'beta',username:'bob',password:'beta-secret',hq:'rtsp://127.0.0.1/source'}],{rtspPort:port}));
  // Empty local publisher paths isolate authorization from cameras/network media.
  for(const name of Object.keys(config.paths))config.paths[name]={source:'publisher'};
  config.rtspAddress='127.0.0.1:'+port;
  const file=join(root,'mediamtx.yml');await writeFile(file,JSON.stringify(config));
  const child=spawn(binary,[file],{windowsHide:true,stdio:'ignore'});const exited=once(child,'exit');
  const request=(path,credentials)=>new Promise((resolve,reject)=>{
    const socket=net.connect(port,'127.0.0.1');let response='';socket.setTimeout(5000,()=>socket.destroy(Error('RTSP timeout')));
    socket.on('error',reject);socket.on('connect',()=>socket.write(`DESCRIBE rtsp://127.0.0.1:${port}/${path} RTSP/1.0\r\nCSeq: 1\r\nAccept: application/sdp\r\n${credentials?'Authorization: Basic '+Buffer.from(credentials).toString('base64')+'\r\n':''}\r\n`));
    socket.on('data',data=>{response+=data.toString();if(response.includes('\r\n\r\n')){socket.destroy();resolve(Number(response.match(/^RTSP\/1.0 (\d+)/)?.[1]));}});
  });
  try{
    let ready=false;for(let i=0;i<60;i++){try{await request('alpha');ready=true;break;}catch{}await new Promise(resolve=>setTimeout(resolve,100));}assert.equal(ready,true,'relay must start with generated config');
    assert.equal(await request('alpha'),401);
    assert.equal(await request('alpha','alice:wrong'),401);
    assert.equal(await request('beta','alice:alpha-secret'),401);
    assert.equal(await request('alpha_lq','alice:alpha-secret'),404,'authorized but no publisher exists');
    assert.equal(await request('alpha','alice:alpha-secret'),404);
    assert.equal(await request('beta','bob:beta-secret'),404);
  }finally{child.kill();await exited;await rm(root,{recursive:true,force:true});}
});
