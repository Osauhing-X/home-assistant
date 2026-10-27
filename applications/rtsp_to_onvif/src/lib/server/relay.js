import { spawn } from 'node:child_process';
import {writePrivateFile,safeRelayLog} from './private-file.js';
import path from 'node:path';
import { cameras, settings } from './store.js';
import { relayConfig } from './relay-config.js';
import { stopChild } from './stop-child.js';

const dir=process.env.RTSP_ONVIF_DATA||path.join(process.env.DATA_DIR||path.resolve('.data'),'application-data','rtsp-to-onvif');
const configFile=path.join(dir,'mediamtx.yml');
let child=null,restarting=Promise.resolve(),available=true,stopping=false;

const stop=()=>stopChild(child);

async function launch(){
  const [all,config]=await Promise.all([cameras(),settings()]);
  await writePrivateFile(configFile, relayConfig(all, config));
  if(!available||stopping)return;
  child=spawn('mediamtx',[configFile],{stdio:['ignore','pipe','pipe']});
  child.stdout.on('data',chunk=>console.log(`[RTSP relay] ${safeRelayLog(chunk.toString().trim())}`));
  child.stderr.on('data',chunk=>console.warn(`[RTSP relay] ${safeRelayLog(chunk.toString().trim())}`));
  child.once('error',error=>{available=false;console.warn(`[RTSP relay] unavailable: ${error.message}`)});
  child.once('exit',code=>{if(code&&available)console.warn(`[RTSP relay] exited with code ${code}`)});
}

export function restartRelay(){if(stopping)return Promise.resolve();restarting=restarting.catch(()=>{}).then(async()=>{await stop();child=null;if(!stopping)await launch()});return restarting}
export function startRelay(){return restartRelay()}
export function stopRelay(){stopping=true;restarting=restarting.catch(()=>{}).then(async()=>{await stop();child=null;});return restarting;}
export function relayRunning(){return Boolean(child&&child.exitCode===null&&available)}
