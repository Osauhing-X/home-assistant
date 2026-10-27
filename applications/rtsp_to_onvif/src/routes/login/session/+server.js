import {redirect} from '@sveltejs/kit';
import {COOKIE,token,SESSION_SECONDS} from '$lib/server/gui-auth.js';
import {attemptGuiLogin} from '$lib/server/gui-login.js';
export async function POST({request,cookies,url,getClientAddress}){
 const result=await attemptGuiLogin({request,address:getClientAddress()});
 if(!result.ok)redirect(303,`/login?${result.reason==='limited'?'limited='+result.retry_after:'invalid=1'}&next=${encodeURIComponent(result.next)}`);
 cookies.set(COOKIE,token(),{path:'/',httpOnly:true,sameSite:'lax',secure:url.protocol==='https:',maxAge:SESSION_SECONDS});redirect(303,result.next);
}
