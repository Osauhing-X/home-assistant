import {rtspConnectClient} from '$lib/server/connect-client.js';
const reply=(body,status=200)=>Response.json(body,{status,headers:{'cache-control':'private, no-store'}});
export function GET(){try{const client=rtspConnectClient();return reply(client?client.view():{enabled:false,status:'disabled'});}catch{return reply({error:'The saved account connection could not be read. Restore its private data and encryption key.'},503);}}
export async function POST({request}){
 const client=rtspConnectClient();if(!client)return reply({error:'Account linking is not enabled on this installation.'},409);
 let input;const reader=request.body?.getReader();if(!reader)return reply({error:'Choose a connection action.'},400);let size=0;const parts=[];
 try{while(true){const {value,done}=await reader.read();if(done)break;size+=value.byteLength;if(size>1024){await reader.cancel();return reply({error:'Request is too large.'},413);}parts.push(value);}input=JSON.parse(Buffer.concat(parts).toString('utf8'));}catch{return reply({error:'Choose a valid connection action.'},400);}finally{reader.releaseLock();}
 if(!['begin','poll','refresh'].includes(input?.action))return reply({error:'Choose a valid connection action.'},400);
 try{return reply(await client[input.action]());}catch{return reply({error:'The account connection could not be completed. Try again; if the problem persists, check the saved connection and encryption key.'},503);}
}
