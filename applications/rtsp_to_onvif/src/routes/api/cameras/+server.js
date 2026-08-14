import { randomUUID } from 'node:crypto';
import { json } from '@sveltejs/kit';
import { cameras, save } from '$lib/server/store.js';

const clean = (input) => ({
  id: String(input.id || randomUUID()).replace(/[^a-zA-Z0-9_-]/g, ''),
  uuid: input.uuid || randomUUID(),
  name: String(input.name || 'Camera').slice(0, 80),
  model: String(input.model || 'RTSP Bridge').slice(0, 80),
  username: String(input.username || 'onvif'),
  password: String(input.password || ''),
  hq: String(input.hq || ''),
  lq: String(input.lq || ''),
  width: Number(input.width) || 1920,
  height: Number(input.height) || 1080,
  fps: Number(input.fps) || 25
});

export async function GET() { return json({ cameras: await cameras() }); }
export async function POST({ request }) { const value=clean(await request.json()),all=await cameras();all.push(value);await save(all);return json(value,{status:201}); }
export async function PUT({ request }) { const value=clean(await request.json()),all=await cameras(),index=all.findIndex(item=>item.id===value.id);if(index<0)return json({error:'Not found'},{status:404});all[index]=value;await save(all);return json(value); }
export async function DELETE({ request }) { const {id}=await request.json();await save((await cameras()).filter(item=>item.id!==id));return json({ok:true}); }
