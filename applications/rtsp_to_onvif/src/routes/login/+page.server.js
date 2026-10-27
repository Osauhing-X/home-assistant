import {fail,redirect} from '@sveltejs/kit';
import {attemptGuiLogin} from '$lib/server/gui-login.js';
import {COOKIE,token,SESSION_SECONDS} from '$lib/server/gui-auth.js';
export const actions={default:async({request,cookies,url,getClientAddress,setHeaders})=>{
 const result=await attemptGuiLogin({request,address:getClientAddress()});
 setHeaders({'cache-control':'private, no-store',...(result.retry_after?{'retry-after':String(result.retry_after)}:{})});
 if(!result.ok)return fail(result.status,{reason:result.reason,retry_after:result.retry_after||0,next:result.next});
 cookies.set(COOKIE,token(),{path:'/',httpOnly:true,sameSite:'lax',secure:url.protocol==='https:',maxAge:SESSION_SECONDS});redirect(303,result.next);
}};
