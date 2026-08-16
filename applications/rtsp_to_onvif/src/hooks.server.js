import { createHash, timingSafeEqual } from 'node:crypto';
import { building } from '$app/environment';
import { redirect } from '@sveltejs/kit';
import { startDiscovery } from '$lib/server/discovery.js';
import { startRelay } from '$lib/server/relay.js';
import { startXEntitiesPublisher } from '$lib/server/x-entities.js';
if(!building){
  startDiscovery();
  startRelay();
  startXEntitiesPublisher();
}
const COOKIE='rtsp_onvif_auth';
const token=()=>createHash('sha256').update(`rtsp-onvif:${process.env.PASSWORD||''}`).digest('hex');
export async function handle({event,resolve}) {
  if (event.url.pathname.startsWith('/onvif/')) {
    const started=Date.now(), body=event.request.method==='POST' ? await event.request.clone().text().catch(()=>'') : '';
    const soapBody=body.match(/<(?:\w+:)?Body(?:\s[^>]*)?>([\s\S]*?)<\/(?:\w+:)?Body>/i)?.[1]||'';
    const action=soapBody.match(/<(?:\w+:)?(Get\w+|Set\w+|Create\w+|Delete\w+)/)?.[1]||'unknown';
    const response=await resolve(event);
    console.log(`[ONVIF] ${event.request.method} ${event.url.pathname} action=${action} status=${response.status} ${Date.now()-started}ms`);
    return response;
  }
  if (event.url.pathname.startsWith('/snapshot/')) return resolve(event);
  if (event.url.pathname === '/update') return resolve(event);
  if (event.url.pathname.startsWith('/login')) return resolve(event);
  const supplied=event.cookies.get(COOKIE)||'', expected=token();
  if (!(supplied.length===expected.length&&timingSafeEqual(Buffer.from(supplied),Buffer.from(expected)))) redirect(303,`/login?next=${encodeURIComponent(event.url.pathname+event.url.search)}`);
  return resolve(event);
}
export { COOKIE, token };
