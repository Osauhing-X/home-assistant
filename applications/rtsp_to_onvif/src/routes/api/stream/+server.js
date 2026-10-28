import {cameras,settings} from '$lib/server/store.js';
import {previewService,PreviewError} from '$lib/server/preview-service.js';
import {readSoapBody} from '$lib/server/soap-body.js';
const json=(data,status=200)=>Response.json(data,{status,headers:{'cache-control':'private, no-store',...(status===503?{'retry-after':'2'}:{})}});
export async function POST({request}){
 try{const input=JSON.parse((await readSoapBody(request,8192)).toString('utf8')),token=previewService.mint(input.stream);return json({url:'/api/stream?token='+token});}
 catch(error){return json({error:error instanceof PreviewError?error.message:'Enter a valid RTSP or RTSPS address.'},error instanceof PreviewError?error.status:400);}
}
export async function GET({url,request}){
 const token=url.searchParams.get('token'),stream=token?previewService.consume(token):(await cameras()).find(item=>item.id===url.searchParams.get('id'))?.hq;
 if(!stream)return json({error:'Stream not found or preview token expired.'},404);
 return previewService.open(stream,await settings(),request.signal);
}
