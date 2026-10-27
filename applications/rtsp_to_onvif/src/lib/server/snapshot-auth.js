import {createHash,createHmac,randomBytes,timingSafeEqual} from 'node:crypto';
import {hasGuiSession} from './gui-auth.js';
const realm='RTSP to ONVIF';
const same=(a,b)=>{const left=Buffer.from(String(a)),right=Buffer.from(String(b));return left.length===right.length&&timingSafeEqual(left,right);};
function fields(header){
 if(typeof header!=='string'||header.length>4096||!/^Digest\s/i.test(header))return null;
 let rest=header.replace(/^Digest\s+/i,''),result={};
 while(rest){
  const match=/^([a-zA-Z][a-zA-Z0-9_-]*)\s*=\s*(?:"((?:[^"\\]|\\["\\])*)"|([^,\s]+))\s*(?:,\s*|$)/.exec(rest);
  if(!match)return null;const name=match[1].toLowerCase();if(Object.hasOwn(result,name))return null;
  result[name]=(match[2]??match[3]).replace(/\\(["\\])/g,'$1');rest=rest.slice(match[0].length);
 }return result;
}
// Stable image URI; RFC 2617 Digest uses the camera's ONVIF credentials.
// MD5 is retained for ONVIF/NVR compatibility, not for password storage.
export function createSnapshotAuth({now=Date.now,nonceKey=randomBytes(32),ttl=300000,maxReplayEntries=2048}={}){
 const used=new Map();
 const sign=(camera,payload)=>createHmac('sha256',nonceKey).update(camera.id+'\0'+payload).digest('hex');
 function challenge(camera){
  const payload=Buffer.from(now()+':'+randomBytes(16).toString('hex')).toString('base64url');
  return `Digest realm="${realm}", nonce="${payload}.${sign(camera,payload)}", algorithm=MD5, qop="auth", charset=UTF-8`;
 }
 return {
  challenge,
  authorized({request,url,cookies,camera}){
   if(hasGuiSession(cookies))return true;
   if(!camera?.id||typeof camera.username!=='string'||!camera.username||typeof camera.password!=='string'||!camera.password)return false;
   const input=fields(request.headers.get('authorization'));
   if(!input||!same(input.username,camera.username)||input.realm!==realm||input.qop!=='auth'||input.uri!==url.pathname+url.search||request.method!=='GET'||
       !/^[0-9a-f]{8}$/i.test(input.nc||'')||parseInt(input.nc,16)<1||!input.cnonce||input.cnonce.length>256)return false;
   const match=/^([A-Za-z0-9_-]+)\.([0-9a-f]{64})$/.exec(input.nonce||'');if(!match||!same(match[2],sign(camera,match[1])))return false;
   const decoded=Buffer.from(match[1],'base64url').toString('utf8'),stamp=/^(\d{10,16}):[0-9a-f]{32}$/.exec(decoded);
   if(!stamp||Number(stamp[1])>now()+5000||Number(stamp[1])+ttl<=now())return false;
   const algorithm=(input.algorithm||'MD5').toUpperCase(),hashName=algorithm==='MD5'?'md5':algorithm==='SHA-256'?'sha256':null;
   if(!hashName||!new RegExp('^[0-9a-f]{'+(hashName==='md5'?32:64)+'}$','i').test(input.response||''))return false;
   const hash=text=>createHash(hashName).update(text).digest('hex');
   const expected=hash(hash(camera.username+':'+realm+':'+camera.password)+':'+input.nonce+':'+input.nc+':'+input.cnonce+':auth:'+hash('GET:'+input.uri));
   if(!same(expected,input.response.toLowerCase()))return false;
   for(const [key,row]of used)if(row.expires<=now())used.delete(key);
   const key=camera.id+':'+input.nonce+':'+input.cnonce,previous=used.get(key),count=parseInt(input.nc,16);
   if(previous&&count<=previous.count||!previous&&used.size>=maxReplayEntries)return false;
   used.set(key,{count,expires:Number(stamp[1])+ttl});return true;
  }
 };
}
