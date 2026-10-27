import test from 'node:test';
import assert from 'node:assert/strict';
import {relayConfig,relayCameraError} from '../src/lib/server/relay-config.js';
const camera = {id: 'camera-1', username: 'owner', password: 'quote"\nsecret', hq: 'rtsp://source/main', lq: 'rtsp://source/low'};
test('relay grants only exact camera read paths, never anonymous or publishing permissions', () => {
  const config = JSON.parse(relayConfig([camera], {}));
  assert.equal(config.authInternalUsers[0].pass, camera.password);
  assert.deepEqual(config.authInternalUsers[0].permissions, [{action:'read',path:'camera-1'},{action:'read',path:'camera-1_lq'}]);
  assert.equal(config.paths['camera-1'].source, camera.hq);
  assert.deepEqual(JSON.parse(relayConfig([], {})).authInternalUsers, []);
  assert.deepEqual(JSON.parse(relayConfig([], {})).paths, {});
});
test('unsafe credentials and conflicting paths fail closed', () => {
  for (const patch of [{username:'any'},{password:''},{id:'bad\npath'},{hq:'http://source'}]) assert.throws(() => relayConfig([{...camera,...patch}], {}));
  assert.throws(() => relayConfig([camera,{...camera,id:'camera-1_lq'}], {}));
});
test('camera validation rejects malformed URLs and stream-path collisions before storage', () => {
  for(const hq of ['rtsp://','rtsp://host\n/path','http://host/path','not a URL']) assert.match(relayCameraError({...camera,hq}),/valid RTSP/);
  assert.match(relayCameraError({...camera,id:'camera-1_lq'},[camera]),/conflicts/);
  assert.equal(relayCameraError({...camera,id:'other',hq:'rtsps://host:322/main'},[camera]),'');
});
