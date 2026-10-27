import {createHash,randomBytes} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {dirname,isAbsolute,join} from 'node:path';
import {createConnectSecrets,writeConnectState} from './connect-secrets.js';

const ORIGIN='https://iseteenindus.oux.ee';
const secret=value=>typeof value==='string'&&/^[A-Za-z0-9_-]{43}$/.test(value);
const email=value=>typeof value==='string'&&value.length<=254&&/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
export function createRtspConnectClient({path=join(process.env.RTSP_ONVIF_DATA||join(process.env.DATA_DIR||process.cwd()+'/.data','application-data','rtsp-to-onvif'),'connect.json'),fetcher=globalThis.fetch,now=Date.now}={}) {
  if(!isAbsolute(path))throw new Error('Connect storage must use an absolute path.');
  const {encryptSecret,decryptSecret}=createConnectSecrets(dirname(path));
  let queue=Promise.resolve();
  function read(){
    let raw;
    try{raw=JSON.parse(readFileSync(path,'utf8'));}catch(error){if(error.code==='ENOENT')return {version:1,local_id:randomBytes(32).toString('base64url'),pending:null,link:null};throw new Error('Connect storage could not be read. Restore the saved file; it was not replaced.');}
    try{
      if(raw.version!==1 || typeof raw.sealed!=='string' || !raw.sealed.startsWith('enc:v1:'))throw new Error();
      const value=JSON.parse(decryptSecret(raw.sealed));
      if(value.version!==1 || value.origin!==ORIGIN || !secret(value.local_id) ||
          (value.pending&&(!secret(value.pending.device_code)||!secret(value.pending.verifier)||!Number.isSafeInteger(value.pending.expires_at))) ||
          (value.link&&(!secret(value.link.credential)||!secret(value.link.id)||!email(value.link.email))))throw new Error();
      return value;
    }catch{throw new Error('Connect storage could not be verified. Restore the saved file and encryption key.');}
  }
  function write(value){
    read();writeConnectState(path,JSON.stringify({version:1,sealed:encryptSecret(JSON.stringify({...value,version:1,origin:ORIGIN}))}));
  }
  function transaction(action){const result=queue.then(action);queue=result.catch(()=>{});return result;}
  function view(value=read()) {
    const pending=value.pending?.expires_at>now()?value.pending:null;
    return {enabled:true,status:value.link?'connected':pending?'awaiting_confirmation':'disconnected',
      account_email:value.link?.email||null,installation_id:value.link?.id||null,
      verification_uri:pending?.verification_uri||null,user_code:pending?.user_code||null,
      expires_at:pending?new Date(pending.expires_at).toISOString():null,
      manage_url:ORIGIN+'/et/connect'};
  }
  async function request(operation,payload,credential){
    const signal=AbortSignal.timeout(10000);
    const response=await fetcher(ORIGIN+'/@_account/connect/'+operation,{method:'POST',redirect:'error',signal,
      headers:{'content-type':'application/json',...(credential?{authorization:'Bearer '+credential}:{})},body:JSON.stringify(payload)});
    if(!response.body)throw new Error('The account service returned an invalid response.');
    const reader=response.body.getReader();const chunks=[];let size=0;
    try{
      while(true){const {value,done}=await reader.read();if(done)break;size+=value.byteLength;if(size>16384){await reader.cancel();throw new Error('Account service response exceeded its size limit.');}chunks.push(value);}
    }finally{reader.releaseLock();}
    let body;try{body=JSON.parse(Buffer.concat(chunks).toString('utf8'));}catch{throw new Error('The account service returned an invalid response.');}
    return {ok:response.ok,status:response.status,body};
  }
  return {
    view,
    begin({name='RTSP to ONVIF'}={}){return transaction(async()=>{
      const value=read();
      if(value.link)throw new Error('This camera relay is already linked. Manage the connection in Iseteenindus.');
      if(value.pending?.expires_at>now())return view(value);
      const installation_id=value.local_id;write(value);
      const verifier=randomBytes(32).toString('base64url');
      const result=await request('begin',{service:'rtsp-to-onvif',installation_id,name,challenge:createHash('sha256').update(verifier).digest('base64url')});
      const flow=result.body;
      let url;try{url=new URL(flow.verification_uri);}catch{throw new Error('The account service is unavailable.');}
      if(!result.ok || !secret(flow.device_code)||!/^[A-F0-9]{4}-[A-F0-9]{4}$/.test(flow.user_code||'') ||
          url.origin!==ORIGIN || url.pathname!=='/et/connect' || url.username || url.password || url.hash ||
          [...url.searchParams.keys()].length!==1 || url.searchParams.get('user_code')!==flow.user_code ||
          !Number.isSafeInteger(flow.expires_in) || flow.expires_in<1 || flow.expires_in>600 ||
          !Number.isSafeInteger(flow.interval) || flow.interval<5 || flow.interval>60)throw new Error('The account service returned an invalid connection request.');
      value.pending={verifier,device_code:flow.device_code,user_code:flow.user_code,verification_uri:url.href,
        expires_at:now()+flow.expires_in*1000,next_poll_at:now()+flow.interval*1000};
      write(value);return view(value);
    });},
    poll(){return transaction(async()=>{
      const value=read();if(value.link)return view(value);
      const pending=value.pending;
      if(!pending || pending.expires_at<=now()){if(pending){value.pending=null;write(value);}return view(value);}
      if(pending.next_poll_at>now())return view(value);
      const result=await request('poll',{device_code:pending.device_code,verifier:pending.verifier});
      pending.next_poll_at=now()+5000;
      if(['invalid_grant','access_denied'].includes(result.body.error)){value.pending=null;write(value);return {...view(value),reason:result.body.error==='access_denied'?'Connection declined.':'Connection request expired. Start again.'};}
      if(result.body.status==='authorization_pending'||result.body.error==='slow_down'){write(value);return view(value);}
      const linked=result.body;
      if(!result.ok || linked.status!=='connected' || !secret(linked.credential) || !secret(linked.installation?.id) ||
          linked.installation.service!=='rtsp-to-onvif' || !email(linked.account?.email))throw new Error('The account connection could not be verified.');
      value.link={credential:linked.credential,id:linked.installation.id,email:linked.account.email,connected_at:new Date(now()).toISOString()};
      value.pending=null;write(value);return view(value);
    });},
    refresh(){return transaction(async()=>{
      const value=read();if(!value.link)return view(value);
      const result=await request('status',{},value.link.credential);
      if(result.status===401){value.link=null;write(value);return {...view(value),reason:'The account connection was removed. Connect again to continue.'};}
      if(!result.ok || result.body.status!=='connected' || result.body.installation?.id!==value.link.id ||
          result.body.installation.service!=='rtsp-to-onvif' || !email(result.body.account?.email))throw new Error('The account connection could not be checked.');
      value.link.email=result.body.account.email;write(value);return view(value);
    });}
  };
}

let configured;
export function rtspConnectClient(){
  if(process.env.RTSP_CONNECT_ENABLED!=='true')return null;
  return configured??=createRtspConnectClient();
}
