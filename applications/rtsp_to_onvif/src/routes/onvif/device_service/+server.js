import { cameras } from '$lib/server/store.js';
import { authenticated, authFault } from '$lib/server/onvif-auth.js';
import { _deviceResponse } from '../[id]/device_service/+server.js';

export async function POST({request,url}) {
  const body=await request.text(), all=await cameras();
  if(!all.length)return new Response('No cameras configured',{status:404});
  if(body.includes('GetSystemDateAndTime'))return _deviceResponse(all[0],body,url);
  const camera=all.find(item=>authenticated(body,item));
  if(!camera){console.warn('[ONVIF] Authentication failed on /onvif/device_service');return authFault()}
  return _deviceResponse(camera,body,url);
}
