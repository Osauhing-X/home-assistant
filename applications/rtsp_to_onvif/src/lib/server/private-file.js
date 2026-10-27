import {randomUUID} from 'node:crypto';
import {mkdir,open,rename,unlink,chmod} from 'node:fs/promises';
import path from 'node:path';
export async function writePrivateFile(destination,source){
 const directory=path.dirname(destination),temporary=destination+'.'+process.pid+'.'+randomUUID()+'.tmp';let descriptor;
 try{
  await mkdir(directory,{recursive:true,mode:0o700});await chmod(directory,0o700);
  descriptor=await open(temporary,'wx',0o600);await descriptor.writeFile(source);await descriptor.sync();await descriptor.close();descriptor=null;
  await rename(temporary,destination);
  if(process.platform!=='win32'){const handle=await open(directory,'r');try{await handle.sync();}finally{await handle.close();}}
 }catch{
  if(descriptor)await descriptor.close().catch(()=>{});await unlink(temporary).catch(()=>{});
  throw Error('RTSP configuration update could not be confirmed. Check the stored configuration before retrying.');
 }
}
export const safeRelayLog=value=>/rtsps?:/i.test(String(value))?'Stream event reported; RTSP source details redacted.':String(value);
