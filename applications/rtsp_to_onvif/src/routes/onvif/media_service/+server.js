import { cameras } from '$lib/server/store.js';
import { authenticated, authFault } from '$lib/server/onvif-auth.js';
import { _mediaResponse } from '../[id]/media_service/+server.js';
export async function POST({request}){const body=await request.text(),camera=(await cameras()).find(item=>authenticated(body,item));if(!camera){console.warn('[ONVIF] Authentication failed on /onvif/media_service');return authFault()}return _mediaResponse(camera,body)}
