import {COOKIE,token,hasGuiSession} from '$lib/server/gui-auth.js';
import { building } from '$app/environment';
import { redirect } from '@sveltejs/kit';
import { startDiscovery,stopDiscovery } from '$lib/server/discovery.js';
import { startRelay,stopRelay } from '$lib/server/relay.js';
import { startXEntitiesPublisher,stopXEntitiesPublisher } from '$lib/server/x-entities.js';
import {readSoapBody} from '$lib/server/soap-body.js';
if(!building&&!(process.env.NODE_ENV==='test'&&process.env.RTSP_ONVIF_OFFLINE_TEST==='true')){
  startDiscovery();
  void startRelay().catch(()=>console.warn('[RTSP relay] Configuration could not be loaded; check stored settings.'));
  startXEntitiesPublisher();
  const shutdown=()=>{stopXEntitiesPublisher();void Promise.allSettled([stopDiscovery(),stopRelay()]);};
  for(const signal of ['SIGTERM','SIGINT'])process.once(signal,shutdown);
}
export async function handle({event,resolve}) {
  if(event.url.pathname.startsWith('//'))return new Response('Invalid path',{status:400});
  const unsafe=!['GET','HEAD','OPTIONS'].includes(event.request.method);
  if(unsafe&&!event.url.pathname.startsWith('/onvif/')&&event.url.pathname!=='/update'&&
      (event.request.headers.get('origin')!==event.url.origin||event.request.headers.get('sec-fetch-site')==='cross-site'))return new Response('Forbidden',{status:403});
  if (event.url.pathname.startsWith('/onvif/')) {
    const started=Date.now();let body='';
    if(event.request.method==='POST'){
      try{const original=event.request,bytes=await readSoapBody(original);body=bytes.toString('utf8');event.request=new Request(original.url,{method:original.method,headers:original.headers,body:bytes,signal:original.signal});}
      catch{return new Response('SOAP request is too large or unreadable.',{status:413,headers:{'cache-control':'private, no-store','connection':'close'}});}
    }
    const soapBody=body.match(/<(?:\w+:)?Body(?:\s[^>]*)?>([\s\S]*?)<\/(?:\w+:)?Body>/i)?.[1]||'';
    const action=soapBody.match(/<(?:\w+:)?(Get\w+|Set\w+|Create\w+|Delete\w+)/)?.[1]||'unknown';
    const response=await resolve(event);
    console.log(`[ONVIF] ${event.request.method} ${event.url.pathname} action=${action} status=${response.status} ${Date.now()-started}ms`);
    return response;
  }
  if (event.url.pathname.startsWith('/snapshot/')) return resolve(event);
  if (event.url.pathname === '/update') return resolve(event);
  if (event.url.pathname.startsWith('/login')) return resolve(event);
  if (!hasGuiSession(event.cookies)) {
    if(event.url.pathname.startsWith('/api/'))return Response.json({error:'Authentication required'},{status:401,headers:{'cache-control':'private, no-store'}});
    redirect(303,`/login?next=${encodeURIComponent(event.url.pathname+event.url.search)}`);
  }
  return resolve(event);
}
export { COOKIE, token };
