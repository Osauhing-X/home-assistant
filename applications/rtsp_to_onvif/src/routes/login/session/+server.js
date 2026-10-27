import {redirect} from '@sveltejs/kit';
import {COOKIE,token} from '$lib/server/gui-auth.js';
function safeNext(value,origin){
 if(typeof value!=='string'||!value.startsWith('/')||value.startsWith('//')||/[\\\u0000-\u001f\u007f]/.test(value))return '/';
 try{const target=new URL(value,origin);return target.origin===origin?target.pathname+target.search+target.hash:'/';}catch{return '/';}
}
export async function POST({request,cookies,url}){
 const form=await request.formData(),password=String(form.get('password')||''),next=safeNext(form.get('next'),url.origin);
 if(!process.env.PASSWORD||password!==process.env.PASSWORD)redirect(303,`/login?invalid=1&next=${encodeURIComponent(next)}`);
 cookies.set(COOKIE,token(),{path:'/',httpOnly:true,sameSite:'lax',secure:url.protocol==='https:',maxAge:604800});redirect(303,next);
}