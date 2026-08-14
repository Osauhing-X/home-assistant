import { spawn } from 'node:child_process';

const cache = new Map();
const safeTarget = (value) => {
  try { const url = new URL(value); return `${url.hostname}:${url.port || 554}${url.pathname}`; }
  catch { return 'invalid-url'; }
};

export async function logStreamDiagnostics(camera, uri, profile) {
  const key = `${camera.id}:${profile}:${uri}`;
  if (Date.now() - (cache.get(key) || 0) < 300_000) return;
  cache.set(key, Date.now());
  const result = await new Promise((resolve) => {
    const child = spawn('ffprobe', ['-v','error','-rtsp_transport','tcp','-select_streams','v:0','-show_entries','stream=codec_name,profile,width,height,r_frame_rate','-of','json',uri], { stdio: ['ignore','pipe','pipe'] });
    const output=[], errors=[];
    const timer=setTimeout(()=>child.kill('SIGKILL'),8000);
    child.stdout.on('data',chunk=>output.push(chunk));
    child.stderr.on('data',chunk=>errors.push(chunk));
    child.once('error',error=>{clearTimeout(timer);resolve({error:error.message})});
    child.once('exit',code=>{clearTimeout(timer);if(code!==0)return resolve({error:Buffer.concat(errors).toString().trim()||`ffprobe exited ${code}`});try{resolve({stream:JSON.parse(Buffer.concat(output).toString()).streams?.[0]})}catch{resolve({error:'Invalid ffprobe response'})}});
  });
  if(result.stream){const stream=result.stream,mismatch=stream.codec_name!=='h264'?' WARNING=UniFi Protect expects an H.264 video profile':'';console.log(`[RTSP] profile=${profile} camera=${camera.name} target=${safeTarget(uri)} reachable=yes codec=${stream.codec_name||'unknown'} resolution=${stream.width||'?'}x${stream.height||'?'} fps=${stream.r_frame_rate||'unknown'}${mismatch}`)}
  else console.warn(`[RTSP] profile=${profile} camera=${camera.name} target=${safeTarget(uri)} reachable=no error=${result.error}`);
}
