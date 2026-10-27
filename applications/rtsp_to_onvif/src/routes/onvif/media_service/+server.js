import {cameras} from '$lib/server/store.js';
import {authenticated,authFault} from '$lib/server/onvif-auth.js';
import {POST as cameraMedia} from '../[id]/media_service/+server.js';
export async function POST({request,url}){
 const body=await request.clone().text(),camera=(await cameras()).find(item=>authenticated(body,item,{consume:false}));
 if(!camera)return authFault();
 return cameraMedia({params:{id:camera.id},request,url});
}
