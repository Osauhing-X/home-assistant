import {createHmac,randomBytes,timingSafeEqual} from 'node:crypto';
export const COOKIE='rtsp_onvif_auth';
export const SESSION_SECONDS=604800;
const signature=(payload,password)=>createHmac('sha256',password).update('rtsp-onvif-session:v1:'+payload).digest('base64url');
export function token(password=process.env.PASSWORD,now=Date.now()) {
 if(typeof password!=='string'||!password.length)return null;
 const issued=Math.floor(now/1000),payload=Buffer.from(JSON.stringify({iat:issued,exp:issued+SESSION_SECONDS,nonce:randomBytes(24).toString('base64url')})).toString('base64url');
 return 'v1.'+payload+'.'+signature(payload,password);
}
export function hasGuiSession(cookies,password=process.env.PASSWORD,now=Date.now()){
 const supplied=cookies?.get(COOKIE);
 if(typeof password!=='string'||!password.length||typeof supplied!=='string'||supplied.length>512)return false;
 const parts=supplied.split('.');if(parts.length!==3||parts[0]!=='v1'||!/^[A-Za-z0-9_-]+$/.test(parts[1])||!/^[A-Za-z0-9_-]{43}$/.test(parts[2]))return false;
 const expected=signature(parts[1],password);if(!timingSafeEqual(Buffer.from(parts[2]),Buffer.from(expected)))return false;
 try{const value=JSON.parse(Buffer.from(parts[1],'base64url').toString('utf8')),seconds=Math.floor(now/1000);
  return Number.isSafeInteger(value.iat)&&Number.isSafeInteger(value.exp)&&value.exp-value.iat===SESSION_SECONDS&&value.iat<=seconds&&value.exp>seconds&&/^[A-Za-z0-9_-]{32}$/.test(value.nonce);
 }catch{return false;}
}
