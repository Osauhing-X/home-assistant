import net from 'node:net';
import os from 'node:os';
import { json } from '@sveltejs/kit';
const localIp=()=>{for(const [name,list] of Object.entries(os.networkInterfaces()))for(const address of list||[])if(address.family==='IPv4'&&!address.internal&&!/^(lo|docker|veth|br-|hassio)/i.test(name))return address.address;return''};
const probe=(host,port)=>new Promise(resolve=>{const socket=net.createConnection({host,port});const done=open=>{socket.destroy();resolve(open)};socket.setTimeout(350);socket.once('connect',()=>done(true));socket.once('timeout',()=>done(false));socket.once('error',()=>done(false))});
export async function POST(){const address=localIp();if(!address)return json({error:'No local IPv4 network was found.'},{status:503});const prefix=address.split('.').slice(0,3).join('.'),ports=[554,8554],found=[];let next=1;const worker=async()=>{while(next<255){const host=`${prefix}.${next++}`;for(const port of ports)if(await probe(host,port)){found.push({host,port,url:`rtsp://${host}:${port}/`});break}}};await Promise.all(Array.from({length:32},worker));return json({network:`${prefix}.0/24`,cameras:found.sort((a,b)=>a.host.localeCompare(b.host,undefined,{numeric:true}))})}
