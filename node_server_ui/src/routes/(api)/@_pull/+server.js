import { exec } from 'child_process';
import { json } from '@sveltejs/kit';


export async function POST({ url }) {
  const name = url.searchParams.get('name');

  exec(`cd /server/app_${name} && git pull --rebase && npm install --omit=dev`);

  return json({ ok: true });
}