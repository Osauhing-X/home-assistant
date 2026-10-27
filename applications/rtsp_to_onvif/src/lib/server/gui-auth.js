import {createHash,timingSafeEqual} from 'node:crypto';
export const COOKIE='rtsp_onvif_auth';
export const token=(password=process.env.PASSWORD)=>typeof password==='string'&&password.length?createHash('sha256').update(`rtsp-onvif:${password}`).digest('hex'):null;
export function hasGuiSession(cookies,password=process.env.PASSWORD){
 const expected=token(password),supplied=cookies?.get(COOKIE);
 return Boolean(expected&&typeof supplied==='string'&&supplied.length===expected.length&&timingSafeEqual(Buffer.from(supplied),Buffer.from(expected)));
}
