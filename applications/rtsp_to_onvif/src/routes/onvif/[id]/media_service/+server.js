import { cameras } from '$lib/server/store.js';
import { authenticated, authFault } from '$lib/server/onvif-auth.js';
import { cameraWithStreamInfo, logStreamDiagnostics } from '$lib/server/stream-diagnostics.js';

const esc=(value)=>String(value).replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[char]));
const xml=body=>new Response(`<?xml version="1.0" encoding="UTF-8"?><env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope" xmlns:tds="http://www.onvif.org/ver10/device/wsdl" xmlns:trt="http://www.onvif.org/ver10/media/wsdl" xmlns:ter="http://www.onvif.org/ver10/error" xmlns:tt="http://www.onvif.org/ver10/schema"><env:Body>${body}</env:Body></env:Envelope>`,{headers:{'content-type':'application/soap+xml; charset=utf-8'}});

export const _profile=(camera,index=0)=>{
  const token=`prof${index}`,suffix=index?String(index):'0';
  return `<trt:Profiles token="${token}" fixed="true"><tt:Name>${index?'SubProfile':'MainProfile'}</tt:Name><tt:VideoSourceConfiguration token="vsrccfg${suffix}"><tt:Name>vsrc</tt:Name><tt:UseCount>1</tt:UseCount><tt:SourceToken>vsrc${suffix}</tt:SourceToken><tt:Bounds x="0" y="0" width="${camera.width}" height="${camera.height}"/></tt:VideoSourceConfiguration><tt:VideoEncoderConfiguration token="venccfg${suffix}"><tt:Name>venc</tt:Name><tt:UseCount>1</tt:UseCount><tt:Encoding>H264</tt:Encoding><tt:Resolution><tt:Width>${camera.width}</tt:Width><tt:Height>${camera.height}</tt:Height></tt:Resolution><tt:Quality>5</tt:Quality><tt:RateControl><tt:FrameRateLimit>${camera.fps}</tt:FrameRateLimit><tt:EncodingInterval>1</tt:EncodingInterval><tt:BitrateLimit>2000</tt:BitrateLimit></tt:RateControl><tt:H264><tt:GovLength>30</tt:GovLength><tt:H264Profile>Baseline</tt:H264Profile></tt:H264><tt:Multicast><tt:Address><tt:Type>IPv4</tt:Type><tt:IPv4Address>0.0.0.0</tt:IPv4Address></tt:Address><tt:Port>0</tt:Port><tt:TTL>1</tt:TTL><tt:AutoStart>false</tt:AutoStart></tt:Multicast><tt:SessionTimeout>PT0S</tt:SessionTimeout></tt:VideoEncoderConfiguration></trt:Profiles>`;
};

export function _mediaResponse(camera,body){
  if(body.includes('GetStreamUri')){const token=body.match(/<(?:\w+:)?ProfileToken>([^<]+)/)?.[1]||'prof0',uri=token==='prof1'&&camera.lq?camera.lq:camera.hq;return xml(`<trt:GetStreamUriResponse><trt:MediaUri><tt:Uri>${esc(uri)}</tt:Uri><tt:InvalidAfterConnect>false</tt:InvalidAfterConnect><tt:InvalidAfterReboot>false</tt:InvalidAfterReboot><tt:Timeout>PT0S</tt:Timeout></trt:MediaUri></trt:GetStreamUriResponse>`)}
  if(body.includes('GetVideoSources'))return xml(`<trt:GetVideoSourcesResponse><trt:VideoSources token="vsrc0"><tt:Framerate>${camera.fps}</tt:Framerate><tt:Resolution><tt:Width>${camera.width}</tt:Width><tt:Height>${camera.height}</tt:Height></tt:Resolution></trt:VideoSources></trt:GetVideoSourcesResponse>`);
  return xml(`<trt:GetProfilesResponse>${_profile(camera,0)}${camera.lq?_profile(camera,1):''}</trt:GetProfilesResponse>`);
}

export async function POST({params,request,url}){
  const camera=(await cameras()).find(item=>item.id===params.id);if(!camera)return new Response('Not found',{status:404});
  const body=await request.text();if(!authenticated(body,camera))return authFault();
  if(body.includes('GetSnapshotUri'))return xml(`<trt:GetSnapshotUriResponse><trt:MediaUri><tt:Uri>${url.protocol}//${url.host}/snapshot/${camera.id}.jpg</tt:Uri><tt:InvalidAfterConnect>false</tt:InvalidAfterConnect><tt:InvalidAfterReboot>false</tt:InvalidAfterReboot><tt:Timeout>PT0S</tt:Timeout></trt:MediaUri></trt:GetSnapshotUriResponse>`);
  if(body.includes('GetStreamUri')){const token=body.match(/<(?:\w+:)?ProfileToken>([^<]+)/)?.[1]||'prof0',uri=token==='prof1'&&camera.lq?camera.lq:camera.hq;void logStreamDiagnostics(camera,uri,token)}
  const profiled=body.includes('GetProfiles')||body.includes('GetVideoSources')?await cameraWithStreamInfo(camera):camera;
  return _mediaResponse(profiled,body);
}
