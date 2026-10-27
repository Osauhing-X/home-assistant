// JSON is a YAML subset: quote every user-controlled key and credential safely.
export function relayConfig(cameras, settings) {
  const paths = Object.create(null), users = [];
  for (const camera of cameras) {
    const names = [camera.id, ...(camera.lq ? [camera.id + '_lq'] : [])];
    if (!/^[A-Za-z0-9_-]+$/.test(camera.id) || names.some(name => Object.hasOwn(paths, name))) throw Error('Invalid or conflicting relay path.');
    if (!camera.username || camera.username === 'any' || !camera.password) throw Error('Set non-empty camera credentials; the reserved username any is not allowed.');
    for (const [index, name] of names.entries()) {
      const source = index ? camera.lq : camera.hq;
      if (!/^rtsps?:\/\//i.test(source || '')) throw Error('Invalid relay source.');
      paths[name] = {source, sourceOnDemand: true, rtspTransport: 'tcp'};
    }
    users.push({user: camera.username, pass: camera.password, ips: [], permissions: names.map(path => ({action: 'read', path}))});
  }
  return JSON.stringify({logLevel: 'warn', authMethod: 'internal', authInternalUsers: users,
    rtsp: true, rtspAddress: ':' + (settings.rtspPort || 8554), rtspTransports: ['tcp'], rtspAuthMethods: ['basic', 'digest'],
    rtmp: false, hls: false, webrtc: false, srt: false, playback: false, api: false, metrics: false, pprof: false, paths}, null, 2);
}
