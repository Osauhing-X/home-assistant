import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { cameras, settings } from './store.js';

const dir=process.env.RTSP_ONVIF_DATA||path.join(process.env.DATA_DIR||path.resolve('.data'),'application-data','rtsp-to-onvif');
const configFile=path.join(dir,'mediamtx.yml');
let child=null,restarting=Promise.resolve(),available=true;

const stop=()=>new Promise(resolve=>{if(!child||child.exitCode!==null)return resolve();const current=child,timer=setTimeout(()=>current.kill('SIGKILL'),3000);current.once('exit',()=>{clearTimeout(timer);resolve()});current.kill('SIGTERM')});

async function launch(){
  const [all,config]=await Promise.all([cameras(),settings()]);
  await mkdir(dir,{recursive:true});
  const paths=all.length?all.flatMap(camera=>[`  ${camera.id}:\n    source: ${JSON.stringify(camera.hq)}\n    sourceOnDemand: true\n    rtspTransport: tcp`,...(camera.lq?[`  ${camera.id}_lq:\n    source: ${JSON.stringify(camera.lq)}\n    sourceOnDemand: true\n    rtspTransport: tcp`]:[])]).join('\n'):'  all:\n    source: publisher';
  await writeFile(configFile,`logLevel: warn\nrtsp: true\nrtspAddress: :${config.rtspPort||8554}\nrtspTransports: [tcp]\nrtmp: false\nhls: false\nwebrtc: false\nsrt: false\nplayback: false\napi: false\nmetrics: false\npprof: false\npaths:\n${paths}\n`);
  if(!available)return;
  child=spawn('mediamtx',[configFile],{stdio:['ignore','pipe','pipe']});
  child.stdout.on('data',chunk=>console.log(`[RTSP relay] ${chunk.toString().trim()}`));
  child.stderr.on('data',chunk=>console.warn(`[RTSP relay] ${chunk.toString().trim()}`));
  child.once('error',error=>{available=false;console.warn(`[RTSP relay] unavailable: ${error.message}`)});
  child.once('exit',code=>{if(code&&available)console.warn(`[RTSP relay] exited with code ${code}`)});
}

export function restartRelay(){restarting=restarting.then(async()=>{await stop();child=null;await launch()});return restarting}
export function startRelay(){return restartRelay()}
export function relayRunning(){return Boolean(child&&child.exitCode===null&&available)}
