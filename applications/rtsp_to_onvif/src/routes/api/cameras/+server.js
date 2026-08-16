import { randomUUID } from 'node:crypto';
import { json } from '@sveltejs/kit';
import { cameras, save } from '$lib/server/store.js';
import { restartRelay } from '$lib/server/relay.js';
import { restartDiscovery } from '$lib/server/discovery.js';
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
  discoveryEnabled: input.discoveryEnabled !== false,
  username: String(input.username || 'onvif'),
  password: String(input.password || ''),
  hq: String(input.hq || ''),
  lq: String(input.lq || ''),
  width: Number(input.width) || 1920,
  height: Number(input.height) || 1080,
  fps: Number(input.fps) || 25
});

export async function GET() { return json({ cameras: (await cameras()).map(camera=>({...camera,discoveryEnabled:camera.discoveryEnabled!==false,assignedIp:assignedIp(camera.id)})) }); }
const invalidIp=(value,all)=>value.ipMode==='static'&&!value.virtualIp?'Choose a valid static IP for this camera.':value.ipMode==='static'&&all.some(item=>item.id!==value.id&&item.ipMode==='static'&&item.virtualIp===value.virtualIp)?`Virtual IP ${value.virtualIp} is already used by another camera.`:'';
const reload=()=>Promise.all([restartRelay(),restartDiscovery()]);
export async function POST({ request }) { const value=clean(await request.json()),all=await cameras(),error=invalidIp(value,all);if(error)return json({error},{status:400});all.push(value);await save(all);await reload();return json(value,{status:201}); }
export async function PUT({ request }) { const value=clean(await request.json()),all=await cameras(),index=all.findIndex(item=>item.id===value.id),error=invalidIp(value,all);if(index<0)return json({error:'Not found'},{status:404});if(error)return json({error},{status:400});all[index]=value;await save(all);await reload();return json(value); }
export async function PATCH({ request }) { const input=await request.json(),all=await cameras(),camera=all.find(item=>item.id===input.id);if(!camera)return json({error:'Not found'},{status:404});if(input.action!=='new-dhcp')return json({error:'Unsupported action'},{status:400});camera.ipMode='dhcp';camera.dhcpIp='';camera.dhcpGeneration=(Number(camera.dhcpGeneration)||0)+1;await save(all);await reload();return json({...camera,assignedIp:assignedIp(camera.id)}); }
export async function DELETE({ request }) { const {id}=await request.json();await save((await cameras()).filter(item=>item.id!==id));await reload();return json({ok:true}); }
