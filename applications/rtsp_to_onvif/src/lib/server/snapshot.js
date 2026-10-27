import {createSnapshotAuth} from './snapshot-auth.js';
const headers={'cache-control':'private, no-store','referrer-policy':'no-referrer','x-content-type-options':'nosniff'};
export function createSnapshotHandler({cameras,spawn,auth=createSnapshotAuth(),timeoutMs=10000,maxBytes=8*1024*1024,maxConcurrent=4}){
 let running=0;
 const reply=(body,status,extra={})=>new Response(body,{status,headers:{...headers,...extra}});
 return async({params,request,url,cookies})=>{
  const camera=(await cameras()).find(item=>item.id===params.id);if(!camera)return reply('Not found',404);
  if(!auth.authorized({camera,request,url,cookies}))return reply('Authentication required',401,{'www-authenticate':auth.challenge(camera)});
  if(request.signal.aborted)return reply('Request cancelled',408);
  if(running>=maxConcurrent)return reply('Snapshot service is busy',503,{'retry-after':'1'});
  try{const source=new URL(camera.hq);if(!['rtsp:','rtsps:'].includes(source.protocol))throw Error();}catch{return reply('Snapshot source is unavailable',502);}
  running++;
  return new Promise(resolve=>{
   let child,timer,finished=false,size=0;const chunks=[];
   const done=(body,status,extra={})=>{if(finished)return;finished=true;clearTimeout(timer);request.signal.removeEventListener('abort',abort);running--;resolve(reply(body,status,extra));};
   const stop=()=>{try{child?.kill('SIGKILL');}catch{}};
   const abort=()=>{stop();done('Request cancelled',408);};
   try{child=spawn('ffmpeg',['-nostdin','-hide_banner','-loglevel','error','-rtsp_transport','tcp','-i',camera.hq,'-frames:v','1','-f','image2pipe','-vcodec','mjpeg','pipe:1'],{stdio:['ignore','pipe','pipe'],windowsHide:true});}
   catch{done('Snapshot failed',502);return;}
   timer=setTimeout(()=>{stop();done('Snapshot timed out',504);},timeoutMs);
   request.signal.addEventListener('abort',abort,{once:true});
   if(request.signal.aborted){abort();return;}
   child.stdout.on('data',chunk=>{if(finished)return;size+=chunk.length;if(size>maxBytes){stop();done('Snapshot exceeds the size limit',502);return;}chunks.push(chunk);});
   // FFmpeg diagnostics may contain the upstream URI/password. Drain, never echo.
   child.stderr.resume();
   child.once('error',()=>done('Snapshot failed',502));
   child.once('close',code=>{const image=Buffer.concat(chunks);if(code!==0||image.length<4||image[0]!==255||image[1]!==216||image.at(-2)!==255||image.at(-1)!==217)done('Snapshot failed',502);else done(image,200,{'content-type':'image/jpeg'});});
  });
 };
}
