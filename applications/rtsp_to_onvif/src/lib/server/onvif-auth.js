import { createHash, timingSafeEqual } from 'node:crypto';

const same = (left, right) => { const a=Buffer.from(String(left)), b=Buffer.from(String(right)); return a.length===b.length && timingSafeEqual(a,b); };
const element=(xml,name)=>{const matches=[...xml.matchAll(new RegExp(`<((?:[\\w.-]+:)?${name})(\\s[^>]*)?>([\\s\\S]*?)<\\/\\1>`, 'g'))];return matches.length===1?{text:matches[0][3],attributes:matches[0][2]||''}:matches.length?false:null;};
const PASSWORD_TYPE='http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#';
const text=value=>value.replace(/&(?:amp|lt|gt|quot|apos);/g,entity=>({'&amp;':'&','&lt;':'<','&gt;':'>','&quot;':'"','&apos;':"'"}[entity]));
export function createOnvifAuthenticator({now=Date.now,windowMs=300000,futureSkewMs=60000,maxNonces=16384}={}){
 const used=new Map();
 return function authenticated(xml,camera,{consume=true}={}){
  if(typeof xml!=='string'||xml.length>65536||/<!DOCTYPE|<!ENTITY/i.test(xml)||typeof camera?.username!=='string'||typeof camera?.password!=='string'||!camera.username||!camera.password)return false;
  const header=element(xml,'Header'),token=header&&element(header.text,'UsernameToken');if(!token)return false;
  const username=element(token.text,'Username'),password=element(token.text,'Password');
  if(!username||!password||/[<>]/.test(username.text+password.text)||!same(text(username.text),camera.username))return false;
  const type=password.attributes.match(/\bType\s*=\s*(["'])(.*?)\1/)?.[2]||'',supplied=text(password.text);
  const nonce=element(token.text,'Nonce'),created=element(token.text,'Created');
  if(nonce===false||created===false)return false;
  if(!nonce&&!created){if(type&&type!==PASSWORD_TYPE+'PasswordText')return false;return same(supplied,camera.password);}
  if(!nonce||!created||(type&&type!==PASSWORD_TYPE+'PasswordDigest'))return false;
  const encoded=nonce.text.replace(/\s/g,'');
  if(!/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(encoded)||!encoded||encoded.length>512)return false;
  const bytes=Buffer.from(encoded,'base64');if(bytes.toString('base64')!==encoded)return false;
  if(!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?(?:Z|[+-]\d{2}:\d{2})$/.test(created.text))return false;
  const timestamp=Date.parse(created.text),clock=now();
  if(!Number.isFinite(timestamp)||timestamp<clock-windowMs||timestamp>clock+futureSkewMs)return false;
  const digest=createHash('sha1').update(Buffer.concat([bytes,Buffer.from(created.text),Buffer.from(camera.password)])).digest('base64');
  if(!same(supplied,digest))return false;
  for(const [key,expiry] of used)if(expiry<=clock)used.delete(key);
  const key=createHash('sha256').update(JSON.stringify([camera.username,camera.password,encoded])).digest('hex');
  if(used.has(key)||used.size>=maxNonces)return false;
  if(consume)used.set(key,timestamp+windowMs+1);
  return true;
 };
}
export const authenticated=createOnvifAuthenticator();

export function authFault() {
  return new Response('<?xml version="1.0"?><s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"><s:Body><s:Fault><s:Code><s:Value>s:Sender</s:Value><s:Subcode><s:Value>ter:NotAuthorized</s:Value></s:Subcode></s:Code><s:Reason><s:Text xml:lang="en">Invalid ONVIF credentials</s:Text></s:Reason></s:Fault></s:Body></s:Envelope>', { status:401, headers:{'content-type':'application/soap+xml; charset=utf-8'} });
}
