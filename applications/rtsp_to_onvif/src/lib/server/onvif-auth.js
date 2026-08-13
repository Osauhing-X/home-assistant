import { createHash, timingSafeEqual } from 'node:crypto';

const value = (xml, name) => xml.match(new RegExp(`<(?:\\w+:)?${name}(?:\\s[^>]*)?>([^<]*)<\\/(?:\\w+:)?${name}>`, 'i'))?.[1] || '';
const same = (left, right) => { const a=Buffer.from(String(left)), b=Buffer.from(String(right)); return a.length===b.length && timingSafeEqual(a,b); };

export function authenticated(xml, camera) {
  const username=value(xml,'Username'), supplied=value(xml,'Password');
  if (!same(username, camera.username)) return false;
  const nonce=value(xml,'Nonce'), created=value(xml,'Created');
  if (nonce && created) {
    const digest=createHash('sha1').update(Buffer.concat([Buffer.from(nonce,'base64'),Buffer.from(created),Buffer.from(camera.password)])).digest('base64');
    return same(supplied,digest);
  }
  return same(supplied,camera.password);
}

export function authFault() {
  return new Response('<?xml version="1.0"?><s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"><s:Body><s:Fault><s:Code><s:Value>s:Sender</s:Value><s:Subcode><s:Value>ter:NotAuthorized</s:Value></s:Subcode></s:Code><s:Reason><s:Text xml:lang="en">Invalid ONVIF credentials</s:Text></s:Reason></s:Fault></s:Body></s:Envelope>', { status:401, headers:{'content-type':'application/soap+xml; charset=utf-8'} });
}
