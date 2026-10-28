import {spawn} from 'node:child_process';

export function createStreamProbe({spawnProcess=spawn,now=Date.now,maxWorkers=2,maxCache=256,ttlMs=300000,timeoutMs=8000,maxBytes=65536}={}){
 const cache=new Map(),pending=new Map(),workers=new Set();let stopped=false;
 const error=message=>({error:message});
 function valid(uri){try{const value=new URL(uri);return typeof uri==='string'&&uri.length<=4096&&!/[\x00-\x20\x7f]/.test(uri)&&['rtsp:','rtsps:'].includes(value.protocol)&&value.hostname;}catch{return false;}}
 function prune(){for(const [uri,row] of cache)if(now()-row.time>=ttlMs)cache.delete(uri);}
 async function probe(uri){
  if(stopped)return error('Stream probing is stopping');
  if(!valid(uri))return error('Invalid RTSP stream address');
  prune();if(cache.has(uri))return {...cache.get(uri).result};
  if(pending.has(uri))return {...await pending.get(uri)};
  if(workers.size>=maxWorkers)return error('Stream probing is busy; try again');
  let child;try{child=spawnProcess('ffprobe',['-v','error','-rtsp_transport','tcp','-select_streams','v:0','-show_entries','stream=codec_name,profile,width,height,r_frame_rate','-of','json',uri],{stdio:['ignore','pipe','pipe']});}catch{return error('Stream probe is unavailable');}
  workers.add(child);
  const operation=new Promise(resolve=>{
   const chunks=[];let bytes=0,finished=false;
   const finish=result=>{if(finished)return;finished=true;clearTimeout(timer);resolve(result);};
   const kill=()=>{try{child.kill('SIGKILL');}catch{}};
   const timer=setTimeout(()=>{kill();finish(error('Stream probe timed out'));},timeoutMs);
   child.stderr.resume();
   child.stdout.on('data',chunk=>{if(finished)return;bytes+=chunk.length;if(bytes>maxBytes){kill();finish(error('Stream probe response is too large'));}else chunks.push(chunk);});
   child.once('error',()=>{if(!child.pid)workers.delete(child);finish(error('Stream probe is unavailable'));});
   child.once('close',code=>{
    workers.delete(child);if(finished)return;
    if(code!==0)return finish(error('Stream probe failed'));
    try{const row=JSON.parse(Buffer.concat(chunks).toString()).streams?.[0];
     if(!row)return finish(error('No video stream'));
     const result={};for(const key of ['codec_name','profile','r_frame_rate'])if(typeof row[key]==='string'&&row[key].length<=100)result[key]=row[key];
     for(const key of ['width','height'])if(Number.isSafeInteger(row[key])&&row[key]>0&&row[key]<=32768)result[key]=row[key];
     const [a,b]=String(result.r_frame_rate||'0/1').split('/').map(Number);result.fps=b?Math.round(a/b):Number(a)||0;if(!Number.isFinite(result.fps)||result.fps<0||result.fps>1000)result.fps=0;
     finish(result);
    }catch{finish(error('Invalid ffprobe response'));}
   });
  });
  pending.set(uri,operation);
  try{const result=await operation;if(!stopped&&!result.error){while(cache.size>=maxCache)cache.delete(cache.keys().next().value);cache.set(uri,{time:now(),result:{...result}});}return {...result};}
  finally{pending.delete(uri);}
 }
 return {probe,stop(){stopped=true;cache.clear();for(const child of workers)try{child.kill('SIGKILL');}catch{}}};
}
export const streamProbe=createStreamProbe();
