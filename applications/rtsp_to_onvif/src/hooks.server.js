import { createHash, timingSafeEqual } from 'node:crypto';
import { redirect } from '@sveltejs/kit';
import { startDiscovery } from '$lib/server/discovery.js';
startDiscovery();
const COOKIE='rtsp_onvif_auth';
const token=()=>createHash('sha256').update(`rtsp-onvif:${process.env.PASSWORD||''}`).digest('hex');
export async function handle({event,resolve}) {
  if (event.url.pathname.startsWith('/onvif/')) return resolve(event);
  if (event.url.pathname.startsWith('/login')) return resolve(event);
  const supplied=event.cookies.get(COOKIE)||'', expected=token();
  if (!(supplied.length===expected.length&&timingSafeEqual(Buffer.from(supplied),Buffer.from(expected)))) redirect(303,`/login?next=${encodeURIComponent(event.url.pathname+event.url.search)}`);
  return resolve(event);
}
export { COOKIE, token };
