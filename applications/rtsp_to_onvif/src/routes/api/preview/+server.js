import { spawn } from 'node:child_process';
import { json } from '@sveltejs/kit';
import { cameras } from '$lib/server/store.js';

async function snapshot(stream) {
  if (!/^rtsps?:\/\//i.test(stream || '')) return json({ error: 'Enter a valid RTSP URL first.' }, { status: 400 });
  return new Promise((resolve) => {
    const child = spawn('ffmpeg', ['-hide_banner','-loglevel','error','-rtsp_transport','tcp','-i',stream,'-frames:v','1','-vf','scale=min(1280\\,iw):-2','-f','image2pipe','-vcodec','mjpeg','pipe:1'], { stdio: ['ignore','pipe','pipe'] });
    const output = [], errors = [];
    const timer = setTimeout(() => child.kill('SIGKILL'), 15000);
    child.stdout.on('data', (chunk) => output.push(chunk));
    child.stderr.on('data', (chunk) => errors.push(chunk));
    child.once('error', (error) => { clearTimeout(timer); resolve(json({ error: error.code === 'ENOENT' ? 'FFmpeg is not installed in the running X add-on. Update/rebuild X Platform 0.9.3 and restart the add-on.' : `Preview unavailable: ${error.message}` }, { status: error.code === 'ENOENT' ? 503 : 502 })); });
    child.once('exit', (code) => {
      clearTimeout(timer);
      const image = Buffer.concat(output);
      if (code === 0 && image.length) resolve(new Response(image, { headers: { 'content-type':'image/jpeg', 'cache-control':'no-store' } }));
      else resolve(json({ error: Buffer.concat(errors).toString().trim() || 'Could not read the RTSP stream within 15 seconds.' }, { status: 502 }));
    });
  });
}

export async function GET({ url }) {
  const camera = (await cameras()).find((item) => item.id === url.searchParams.get('id'));
  if (!camera) return json({ error: 'Camera not found.' }, { status: 404 });
  return snapshot(camera.hq);
}

export async function POST({ request }) {
  const { stream } = await request.json();
  return snapshot(String(stream || ''));
}
