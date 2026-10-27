import { spawn } from 'node:child_process';

const cache = new Map();
const safeTarget = (value) => { try { const url=new URL(value);return `${url.hostname}:${url.port||554}`; } catch { return 'invalid-url'; } };
const frameRate = (value) => { const [a,b]=String(value||'0/1').split('/').map(Number);return b?Math.round(a/b):Number(a)||0; };

export async function probeStream(uri) { if(process.env.NODE_ENV==='test'&&process.env.RTSP_ONVIF_OFFLINE_TEST==='true')return {error:'Stream probing is disabled in offline tests'};
  const cached=cache.get(uri);if(cached&&Date.now()-cached.time<300_000)return cached.result;
  const result=await new Promise((resolve)=>{const child=spawn('ffprobe',['-v','error','-rtsp_transport','tcp','-select_streams','v:0','-show_entries','stream=codec_name,profile,width,height,r_frame_rate','-of','json',uri],{stdio:['ignore','pipe','pipe']}),output=[],timer=setTimeout(()=>child.kill('SIGKILL'),8000);child.stdout.on('data',chunk=>output.push(chunk));child.stderr.resume();child.once('error',error=>{clearTimeout(timer);resolve({error:'Stream probe is unavailable'})});child.once('exit',code=>{clearTimeout(timer);if(code!==0)return resolve({error:'Stream probe failed'});try{const stream=JSON.parse(Buffer.concat(output).toString()).streams?.[0];resolve(stream?{...stream,fps:frameRate(stream.r_frame_rate)}:{error:'No video stream'})}catch{resolve({error:'Invalid ffprobe response'})}})});
  cache.set(uri,{time:Date.now(),result});return result;
}

export async function cameraWithStreamInfo(camera) { const stream=await probeStream(camera.hq);return stream.error?camera:{...camera,width:stream.width||camera.width,height:stream.height||camera.height,fps:stream.fps||camera.fps,codec:stream.codec_name||'h264'}; }
export async function logStreamDiagnostics(camera,uri,profile) { if(process.env.NODE_ENV==='test'&&process.env.RTSP_ONVIF_OFFLINE_TEST==='true')return; const stream=await probeStream(uri);if(!stream.error){const mismatch=stream.codec_name!=='h264'?' WARNING=UniFi Protect expects an H.264 video profile':'';console.log(`[RTSP] profile=${profile} camera=${camera.name} target=${safeTarget(uri)} reachable=yes codec=${stream.codec_name||'unknown'} resolution=${stream.width||'?'}x${stream.height||'?'} fps=${stream.r_frame_rate||'unknown'}${mismatch}`)}else console.warn(`[RTSP] profile=${profile} camera=${camera.name} target=${safeTarget(uri)} reachable=no error=${stream.error}`); }
