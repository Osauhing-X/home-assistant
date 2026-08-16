import { randomUUID } from 'node:crypto';
import { json } from '@sveltejs/kit';
import { cameras, save } from '$lib/server/store.js';
import { restartRelay } from '$lib/server/relay.js';
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

export async function GET() { return json({ cameras: (await cameras()).map(camera=>({...camera,discoveryMode:advertised(camera)?camera.discoveryMode||'always':'off',discoveryEnabled:advertised(camera),assignedIp:assignedIp(camera.id)})) }); }
const invalidIp=(value,all)=>value.ipMode==='static'&&!value.virtualIp?'Choose a valid static IP for this camera.':value.ipMode==='static'&&all.some(item=>item.id!==value.id&&item.ipMode==='static'&&item.virtualIp===value.virtualIp)?`Virtual IP ${value.virtualIp} is already used by another camera.`:'';
const reload=()=>Promise.all([restartRelay(),restartDiscovery()]);
export async function POST({ request }) { const value=prepareDiscovery(clean(await request.json())),all=await cameras(),error=invalidIp(value,all);if(error)return json({error},{status:400});all.push(value);await save(all);await reload();return json(value,{status:201}); }
export async function PUT({ request }) { const value=clean(await request.json()),all=await cameras(),index=all.findIndex(item=>item.id===value.id),error=invalidIp(value,all);if(index<0)return json({error:'Not found'},{status:404});if(error)return json({error},{status:400});const previous=all[index],wasAdvertised=advertised(previous);prepareDiscovery(value,previous);all[index]=value;await save(all);if(wasAdvertised&&!advertised(value))await announceBye(value).catch(error=>console.warn('[WS-Discovery Bye]',error.message));await reload();return json(value); }
export async function PATCH({ request }) { const input=await request.json(),all=await cameras(),camera=all.find(item=>item.id===input.id);if(!camera)return json({error:'Not found'},{status:404});if(input.action!=='new-dhcp')return json({error:'Unsupported action'},{status:400});camera.ipMode='dhcp';camera.dhcpIp='';camera.dhcpGeneration=(Number(camera.dhcpGeneration)||0)+1;await save(all);await reload();return json({...camera,assignedIp:assignedIp(camera.id)}); }
export async function DELETE({ request }) { const {id}=await request.json(),all=await cameras(),camera=all.find(item=>item.id===id);if(camera?.discoveryEnabled!==false)await announceBye(camera).catch(error=>console.warn('[WS-Discovery Bye]',error.message));await save(all.filter(item=>item.id!==id));await reload();return json({ok:true}); }
