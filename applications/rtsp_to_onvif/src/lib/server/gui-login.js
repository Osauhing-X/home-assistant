import {createHash,timingSafeEqual} from 'node:crypto';
import {guiLoginLimit} from './login-limit.js';
import {readSoapBody as readFormBody} from './soap-body.js';
export function safeNext(value,origin){
 if(typeof value!=='string'||value.length>2048||!value.startsWith('/')||value.startsWith('//')||/[\\\u0000-\u001f\u007f]/.test(value))return '/';
 try{const target=new URL(value,origin);return target.origin===origin?target.pathname+target.search+target.hash:'/';}catch{return '/';}
}
export async function attemptGuiLogin({request,address,password=process.env.PASSWORD,limit=guiLoginLimit}){
 const gate=limit.check(address);if(!gate.allowed)return {ok:false,status:429,reason:'limited',retry_after:gate.retry_after,next:safeNext(new URL(request.url).searchParams.get('next'),new URL(request.url).origin)};
 let form;try{const type=request.headers.get('content-type')||'';if(!/^(?:application\/x-www-form-urlencoded(?:;|$)|multipart\/form-data;)/i.test(type))throw Error();const bytes=await readFormBody(request,16384);form=await new Request(request.url,{method:'POST',headers:request.headers,body:bytes}).formData();}catch{return {ok:false,status:400,reason:'invalid_request',next:'/'};}
 const next=safeNext(form.get('next'),new URL(request.url).origin),supplied=form.get('password');
 const valid=typeof password==='string'&&password.length>0&&typeof supplied==='string'&&timingSafeEqual(createHash('sha256').update(supplied).digest(),createHash('sha256').update(password).digest());
 if(!valid){const result=limit.failure(address);return {ok:false,status:result.allowed?400:429,reason:result.allowed?'invalid':'limited',retry_after:result.retry_after,next};}
 limit.success(address);return {ok:true,next};
}
