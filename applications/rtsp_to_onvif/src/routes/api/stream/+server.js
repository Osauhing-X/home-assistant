import { spawn } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { json } from '@sveltejs/kit';
import { cameras, settings } from '$lib/server/store.js';

const temporary = new Map();
export async function POST({ request }) {
  const { stream } = await request.json();
  if (!/^rtsps?:\/\//i.test(stream || '')) return json({ error: 'Enter a valid RTSP URL first.' }, { status: 400 });
  const token=randomUUID(); temporary.set(token,{stream:String(stream),expires:Date.now()+60000});
  return json({ url:`/api/stream?token=${token}` });
}
export async function GET({ url, request }) {
  let stream=''; const token=url.searchParams.get('token');
  if(token){const entry=temporary.get(token);if(entry&&entry.expires>Date.now())stream=entry.stream;temporary.delete(token)}
  else stream=(await cameras()).find(item=>item.id===url.searchParams.get('id'))?.hq||'';
  if(!stream)return json({error:'Stream not found or preview token expired.'},{status:404});
  const config=await settings(),lowLatency=config.buffering?[]:['-fflags','nobuffer','-flags','low_delay','-analyzeduration','0','-probesize','16384'];
  const child=spawn('ffmpeg',['-hide_banner','-loglevel','error',...lowLatency,'-rtsp_transport','tcp','-i',stream,'-an','-c:v','libx264','-preset','ultrafast','-tune','zerolatency','-g',String(config.gop),'-keyint_min',String(config.gop),'-sc_threshold','0','-bf','0','-flush_packets','1','-movflags','frag_keyframe+empty_moov+default_base_moof','-frag_duration',String(config.fragmentMs*1000),'-f','mp4','pipe:1'],{stdio:['ignore','pipe','pipe']});
  request.signal.addEventListener('abort',()=>child.kill('SIGKILL'),{once:true});
  let closed=false;
  const body=new ReadableStream({start(controller){child.stdout.on('data',chunk=>{if(!closed)try{controller.enqueue(chunk)}catch{closed=true;child.kill('SIGKILL')}});child.once('error',error=>{if(!closed){closed=true;try{controller.error(error)}catch{}}});child.once('exit',()=>{if(!closed){closed=true;try{controller.close()}catch{}}})},cancel(){closed=true;child.kill('SIGKILL')}});
  return new Response(body,{headers:{'content-type':'video/mp4','cache-control':'no-store'}});
}
