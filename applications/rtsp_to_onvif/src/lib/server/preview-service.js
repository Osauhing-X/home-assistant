import {spawn} from 'node:child_process';
import {randomUUID} from 'node:crypto';
import {stopChild} from './stop-child.js';
export const validStream=value=>{if(typeof value!=='string'||value.length>4096||/[\u0000-\u001f\u007f]/.test(value))return false;try{const url=new URL(value);return ['rtsp:','rtsps:'].includes(url.protocol)&&Boolean(url.hostname);}catch{return false;}};
export class PreviewError extends Error{constructor(status,message){super(message);this.status=status;}}
const failure=(status,error)=>Response.json({error},{status,headers:{'cache-control':'private, no-store',...(status===503?{'retry-after':'2'}:{})}});
export function createPreviewService({spawnProcess=spawn,now=Date.now,maxWorkers=2,maxTokens=256,tokenTtlMs=60000,startupMs=10000,durationMs=300000,queueBytes=262144}={}){
 const tokens=new Map(),workers=new Map();let stopping=false;
 const purge=()=>{for(const [key,row] of tokens)if(row.expires<=now())tokens.delete(key);};
 return {
  mint(stream){purge();if(!validStream(stream))throw new PreviewError(400,'Enter a valid RTSP or RTSPS address.');if(stopping||workers.size>=maxWorkers)throw new PreviewError(503,'Preview slots are busy. Close another preview and try again.');if(tokens.size>=maxTokens)throw new PreviewError(429,'Too many preview requests. Wait a minute and try again.');const token=randomUUID();tokens.set(token,{stream,expires:now()+tokenTtlMs});return token;},
  consume(token){purge();const row=tokens.get(token);tokens.delete(token);return row?.stream||'';},
  open(stream,config,signal){
   if(!validStream(stream))return failure(400,'Enter a valid RTSP or RTSPS address.');
   if(stopping||workers.size>=maxWorkers)return failure(503,'Preview slots are busy. Close another preview and try again.');
   if(signal?.aborted)return failure(400,'The preview request was closed.');
   const low=config.buffering?[]:['-fflags','nobuffer','-flags','low_delay','-analyzeduration','0','-probesize','16384'];let child;
   try{child=spawnProcess('ffmpeg',['-hide_banner','-loglevel','error',...low,'-rtsp_transport','tcp','-threads','1','-i',stream,'-an','-c:v','libx264','-threads','1','-preset','ultrafast','-tune','zerolatency','-g',String(config.gop||5),'-keyint_min',String(config.gop||5),'-sc_threshold','0','-bf','0','-flush_packets','1','-movflags','frag_keyframe+empty_moov+default_base_moof','-frag_duration',String((config.fragmentMs||100)*1000),'-f','mp4','pipe:1'],{stdio:['ignore','pipe','pipe']});}catch{return failure(503,'Camera preview is unavailable.');}
   let controller,closed=false,received=false,startTimer,endTimer;
   const kill=()=>{try{child.kill('SIGKILL');}catch{}};
   const finish=(error,terminate=false)=>{if(closed)return;closed=true;clearTimeout(startTimer);clearTimeout(endTimer);signal?.removeEventListener('abort',abort);if(terminate)kill();try{error?controller?.error(Error('Camera preview stopped. Check the source and try again.')):controller?.close();}catch{}};
   const abort=()=>finish(true,true);
   workers.set(child,()=>finish(false,true));child.stderr.resume();
   child.once('error',()=>{finish(true,true);if(!child.pid)workers.delete(child);});
   child.once('close',code=>{finish(code!==0);workers.delete(child);});
   const body=new ReadableStream({start(value){controller=value;child.stdout.on('data',chunk=>{if(closed)return;received=true;clearTimeout(startTimer);try{controller.enqueue(chunk);if(controller.desiredSize<=0)child.stdout.pause();}catch{finish(true,true);}});},pull(){if(!closed)child.stdout.resume();},cancel(){finish(false,true);}},{highWaterMark:queueBytes,size:chunk=>chunk.byteLength});
   signal?.addEventListener('abort',abort,{once:true});
   startTimer=setTimeout(()=>{if(!received)finish(true,true);},startupMs);endTimer=setTimeout(()=>finish(false,true),durationMs);
   return new Response(body,{headers:{'content-type':'video/mp4','cache-control':'private, no-store','accept-ranges':'none','referrer-policy':'no-referrer'}});
  },
  async stop(){stopping=true;tokens.clear();for(const stop of workers.values())stop();await Promise.all([...workers.keys()].map(child=>stopChild(child)));}
 };
}
export const previewService=createPreviewService();
