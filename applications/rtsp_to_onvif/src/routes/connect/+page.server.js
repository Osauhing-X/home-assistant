import {rtspConnectClient} from '$lib/server/connect-client.js';
export function load({setHeaders}){
 setHeaders({'cache-control':'private, no-store'});
 try{const client=rtspConnectClient();return {connection:client?client.view():{enabled:false,status:'disabled'},error:''};}
 catch{return {connection:null,error:'The saved account connection could not be read. Restore its private data and encryption key.'};}
}
