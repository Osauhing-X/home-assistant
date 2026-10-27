import { randomUUID } from 'node:crypto';
import { json } from '@sveltejs/kit';
import { cameras, updateCameras } from '$lib/server/store.js';
import { restartRelay } from '$lib/server/relay.js';
import { relayCameraError } from '$lib/server/relay-config.js';
import { announceBye, restartDiscovery } from '$lib/server/discovery.js';
import { assignedIp } from '$lib/server/network-aliases.js';

const clean = (input) => ({
  id: String(input.id || randomUUID()).replace(/[^a-zA-Z0-9_-]/g, ''),
  uuid: input.uuid || randomUUID(),
  name: String(input.name || 'Camera').slice(0, 80),
  model: String(input.model || 'RTSP Bridge').slice(0, 80),
  ipMode: input.ipMode === 'static' ? 'static' : 'dhcp',
  virtualIp: /^((25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(25[0-5]|2[0-4]\d|1?\d?\d)$/.test(String(input.virtualIp||'')) ? String(input.virtualIp) : '',
  dhcpIp: /^((25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(25[0-5]|2[0-4]\d|1?\d?\d)$/.test(String(input.dhcpIp||'')) ? String(input.dhcpIp) : '',
  dhcpGeneration: Math.max(0,Number(input.dhcpGeneration)||0),
  discoveryMode: ['on_connect','always','10m','30m','1h','2h','3h','12h','off'].includes(input.discoveryMode) ? input.discoveryMode : input.discoveryEnabled===false?'off':'on_connect',
  discoveryUntil: Number(input.discoveryUntil)||0,
  username: String(input.username || 'onvif'),
  password: String(input.password || ''),
  hq: String(input.hq || ''),
  lq: String(input.lq || ''),
  width: Number(input.width) || 1920,
  height: Number(input.height) || 1080,
  fps: Number(input.fps) || 25
});

const discoveryMs={ '10m':10*60e3,'30m':30*60e3,'1h':60*60e3,'2h':2*60*60e3,'3h':3*60*60e3,'12h':12*60*60e3 };
const prepareDiscovery=(value,previous)=>{if(discoveryMs[value.discoveryMode]&&(!previous||previous.discoveryMode!==value.discoveryMode||value.discoveryUntil<=Date.now()))value.discoveryUntil=Date.now()+discoveryMs[value.discoveryMode];else if(!discoveryMs[value.discoveryMode])value.discoveryUntil=0;value.discoveryEnabled=value.discoveryMode!=='off';return value};
const advertised=camera=>camera.discoveryMode?camera.discoveryMode!=='off'&&(!discoveryMs[camera.discoveryMode]||Number(camera.discoveryUntil)>Date.now()):camera.discoveryEnabled!==false;
const streamIdentity=(value)=>{try{const url=new URL(String(value||''));url.username='';url.password='';url.hostname=url.hostname.toLowerCase();url.pathname=url.pathname.replace(/\/+$/,'')||'/';return url.toString()}catch{return String(value||'').trim().toLowerCase()}};

export async function GET() { return json({ cameras: (await cameras()).map(camera=>({...camera,discoveryMode:advertised(camera)?camera.discoveryMode||'always':'off',discoveryEnabled:advertised(camera),assignedIp:assignedIp(camera.id)})) }); }
const invalidCamera=(value,all)=>!value.username||!value.password?'Set a non-empty ONVIF username and password.':value.ipMode==='static'&&!value.virtualIp?'Choose a valid static IP for this camera.':value.ipMode==='static'&&all.some(item=>item.id!==value.id&&item.ipMode==='static'&&item.virtualIp===value.virtualIp)?`Virtual IP ${value.virtualIp} is already used by another camera.`:all.some(item=>item.id!==value.id&&item.uuid===value.uuid)?'This ONVIF device identity is already used by another camera.':all.some(item=>item.id!==value.id&&streamIdentity(item.hq)===streamIdentity(value.hq))?'This RTSP camera is already configured.':'';
const reload=()=>Promise.all([restartRelay(),restartDiscovery()]);
export async function POST({request}){
 const value=prepareDiscovery(clean(await request.json()));
 const response=await updateCameras(all=>{const error=relayCameraError(value,all)||invalidCamera(value,all);if(error)return json({error},{status:409});all.push(value);return json(value,{status:201});});
 if(response.status===201)await reload();return response;
}
export async function PUT({request}){
 const value=clean(await request.json());let bye;
 const response=await updateCameras(all=>{const index=all.findIndex(item=>item.id===value.id),error=relayCameraError(value,all.filter(item=>item.id!==value.id))||invalidCamera(value,all);if(index<0)return json({error:'Not found'},{status:404});if(error)return json({error},{status:409});const previous=all[index],wasAdvertised=advertised(previous);prepareDiscovery(value,previous);all[index]=value;if(wasAdvertised&&!advertised(value))bye=value;return json(value);});
 if(response.status===200){if(bye)await announceBye(bye).catch(error=>console.warn('[WS-Discovery Bye]',error.message));await reload();}return response;
}
export async function PATCH({request}){
 const input=await request.json();
 const response=await updateCameras(all=>{const camera=all.find(item=>item.id===input.id);if(!camera)return json({error:'Not found'},{status:404});if(input.action!=='new-dhcp')return json({error:'Unsupported action'},{status:400});camera.ipMode='dhcp';camera.dhcpIp='';camera.dhcpGeneration=(Number(camera.dhcpGeneration)||0)+1;return json({...camera,assignedIp:assignedIp(camera.id)});});
 if(response.status===200)await reload();return response;
}
export async function DELETE({request}){
 const {id}=await request.json();let bye;
 await updateCameras(all=>{const index=all.findIndex(item=>item.id===id);if(index<0)return;if(all[index].discoveryEnabled!==false)bye=all[index];all.splice(index,1);});
 if(bye)await announceBye(bye).catch(error=>console.warn('[WS-Discovery Bye]',error.message));await reload();return json({ok:true});
}
