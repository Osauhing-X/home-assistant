import dgram from 'node:dgram';
import http from 'node:http';
import os from 'node:os';
import { cameras, saveDhcpLeases, settings } from './store.js';
import { clearAliases, syncAliases } from './network-aliases.js';

let socket=null,proxy=null,restarting=Promise.resolve(),signalsBound=false,currentHost='',assigned=new Map();
const ip=()=>{for(const [name,list] of Object.entries(os.networkInterfaces()))for(const address of list||[])if(address.family==='IPv4'&&!address.internal&&!/^(lo|docker|veth|br-|hassio|vmnet|vboxnet|xov)/i.test(name))return address.address;return'127.0.0.1'};
const esc=value=>String(value).replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[char]));
const close=server=>new Promise(resolve=>server?server.close(()=>resolve()):resolve());
const destination=request=>String(request.socket.localAddress||'').replace(/^::ffff:/,'');
const byeEnvelope=camera=>`<?xml version="1.0"?><s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:a="http://www.w3.org/2005/08/addressing" xmlns:d="http://schemas.xmlsoap.org/ws/2005/04/discovery"><s:Header><a:MessageID>urn:uuid:${crypto.randomUUID()}</a:MessageID><a:To s:mustUnderstand="1">urn:schemas-xmlsoap-org:ws:2005:04:discovery</a:To><a:Action s:mustUnderstand="1">http://schemas.xmlsoap.org/ws/2005/04/discovery/Bye</a:Action></s:Header><s:Body><d:Bye><a:EndpointReference><a:Address>urn:uuid:${camera.uuid}</a:Address></a:EndpointReference></d:Bye></s:Body></s:Envelope>`;

export async function announceBye(camera){const config=await settings(),message=Buffer.from(byeEnvelope(camera));await new Promise((resolve,reject)=>{const bye=dgram.createSocket('udp4');bye.once('error',error=>{bye.close();reject(error)});bye.bind(0,()=>{try{bye.setMulticastTTL(2);bye.send(message,config.discoveryPort,'239.255.255.250',error=>{bye.close();error?reject(error):resolve()})}catch(error){bye.close();reject(error)}})});console.log(`[WS-Discovery] ${camera.name} Bye announced; it is no longer advertised.`)}

async function bind(){
  const config=await settings(),all=await cameras(),host=ip(),appPort=Number(process.env.PORT||8090);currentHost=host;
  assigned=await syncAliases(all,host);
  await saveDhcpLeases(assigned);
  if(config.onvifPort===appPort)throw new Error('ONVIF port must differ from the application GUI port.');

  proxy=http.createServer((request,response)=>{
    const targetHost=destination(request),camera=all.find(item=>assigned.get(item.id)===targetHost);
    let targetPath=request.url;
    if(camera){
      if(/^\/onvif\/device_service(?:\?|$)/.test(targetPath))targetPath=targetPath.replace('/onvif/device_service',`/onvif/${camera.id}/device_service`);
      if(/^\/onvif\/media_service(?:\?|$)/.test(targetPath))targetPath=targetPath.replace('/onvif/media_service',`/onvif/${camera.id}/media_service`);
    }
    const upstream=http.request({hostname:'127.0.0.1',port:appPort,path:targetPath,method:request.method,headers:{...request.headers,host:`${targetHost}:${config.onvifPort}`}},result=>{response.writeHead(result.statusCode||502,result.headers);result.pipe(response)});
    upstream.on('error',error=>{response.statusCode=502;response.end(error.message)});request.pipe(upstream);
  });
  proxy.on('error',error=>console.error('[ONVIF proxy]',error.message));proxy.listen(config.onvifPort,'0.0.0.0');

  if(!config.autoDiscovery)return;
  socket=dgram.createSocket({type:'udp4',reuseAddr:true});
  socket.on('message',async(message,rinfo)=>{
    const body=message.toString();if(!body.includes('Probe')||!body.includes('NetworkVideoTransmitter'))return;
    const match=body.match(/<(?:\w+:)?MessageID>([^<]+)/),seen=new Set();
    for(const camera of await cameras()){
      if(camera.discoveryEnabled===false)continue;
      const cameraHost=assigned.get(camera.id);
      if(!cameraHost){console.warn(`[WS-Discovery] ${camera.name} skipped: no virtual IP is assigned.`);continue}
      if(seen.has(cameraHost)){console.warn(`[WS-Discovery] ${camera.name} skipped: IP ${cameraHost} is already used by another virtual camera.`);continue}seen.add(cameraHost);
      const response=`<?xml version="1.0"?><s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:a="http://www.w3.org/2005/08/addressing" xmlns:d="http://schemas.xmlsoap.org/ws/2005/04/discovery" xmlns:dn="http://www.onvif.org/ver10/network/wsdl"><s:Header><a:MessageID>urn:uuid:${crypto.randomUUID()}</a:MessageID><a:RelatesTo>${esc(match?.[1]||'')}</a:RelatesTo><a:To s:mustUnderstand="1">http://schemas.xmlsoap.org/ws/2005/04/discovery/ProbeMatches</a:To><a:Action s:mustUnderstand="1">http://schemas.xmlsoap.org/ws/2005/04/discovery/ProbeMatches</a:Action></s:Header><s:Body><d:ProbeMatches><d:ProbeMatch><a:EndpointReference><a:Address>urn:uuid:${camera.uuid}</a:Address></a:EndpointReference><d:Types>dn:NetworkVideoTransmitter</d:Types><d:Scopes>onvif://www.onvif.org/type/NetworkVideoTransmitter onvif://www.onvif.org/type/video_encoder onvif://www.onvif.org/name/${encodeURIComponent(camera.name)} onvif://www.onvif.org/hardware/${encodeURIComponent(camera.model)}</d:Scopes><d:XAddrs>http://${cameraHost}:${config.onvifPort}/onvif/device_service</d:XAddrs><d:MetadataVersion>4</d:MetadataVersion></d:ProbeMatch></d:ProbeMatches></s:Body></s:Envelope>`;
      socket.send(Buffer.from(response),rinfo.port,rinfo.address);
    }
  });
  socket.on('error',error=>console.error('[WS-Discovery]',error.message));socket.bind(config.discoveryPort,()=>socket.addMembership('239.255.255.250'));
}

export function restartDiscovery(){restarting=restarting.then(async()=>{await Promise.all([close(socket),close(proxy)]);socket=null;proxy=null;await bind()}).catch(error=>console.error('[ONVIF discovery]',error.message));return restarting}
export function startDiscovery(){if(!signalsBound){signalsBound=true;for(const signal of ['SIGTERM','SIGINT'])process.once(signal,()=>{void clearAliases(currentHost)})}return restartDiscovery()}
export function discoveryRunning(){return Boolean(socket||proxy)}
