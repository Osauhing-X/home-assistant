import test from 'node:test';
import assert from 'node:assert/strict';
import {runtimeOptions} from './runtime-options.mjs';
const options={password:'synthetic-password-only',port:8090,public_origin:'http://192.168.1.20:8090'};
test('standalone options use isolated persistent state and an explicit origin',()=>{
 const env=runtimeOptions(options);assert.equal(env.ORIGIN,options.public_origin);assert.equal(env.PORT,'8090');assert.equal(env.RTSP_CONNECT_ENABLED,'true');assert.equal(env.RTSP_ONVIF_DATA,'/data/application-data/rtsp-to-onvif');assert.equal(env.NODE_ENV,'production');
});
test('invalid addon options fail without including entered secrets in errors',()=>{
 for(const patch of [{password:''},{port:80},{port:'8090'},{public_origin:'http://user:secret@host/'},{public_origin:'http://host/path'},{public_origin:'http://host/?token=secret'},{public_origin:'ftp://host'},{public_origin:'http://0.0.0.0'}]){
  assert.throws(()=>runtimeOptions({...options,...patch}),error=>!error.message.includes('synthetic-password')&&!error.message.includes('user:secret'));
 }
});
