import {createCipheriv,createDecipheriv,randomBytes} from 'node:crypto';
import {readFileSync,mkdirSync,openSync,writeFileSync,fsyncSync,closeSync,renameSync,chmodSync,unlinkSync} from 'node:fs';
import {dirname,join} from 'node:path';

export function writeConnectState(path,content){
 const directory=dirname(path),temporary=path+'.'+randomBytes(12).toString('hex')+'.tmp';let fd;
 try{mkdirSync(directory,{recursive:true,mode:0o700});chmodSync(directory,0o700);fd=openSync(temporary,'wx',0o600);writeFileSync(fd,content);fsyncSync(fd);closeSync(fd);fd=undefined;renameSync(temporary,path);
  if(process.platform!=='win32'){fd=openSync(directory,'r');fsyncSync(fd);closeSync(fd);fd=undefined;}
 }catch{if(fd!==undefined)try{closeSync(fd);}catch{}try{unlinkSync(temporary);}catch{}throw Error('Connect storage could not be saved.');}
}
export function createConnectSecrets(directory){
 const path=join(directory,'.connect-key');
 function key(create=false){
  try{const value=readFileSync(path);if(value.length!==32)throw Error();return value;}
  catch(error){if(error.code!=='ENOENT'||!create)throw Error('Connect encryption key is missing or invalid. Restore it from backup.');}
  mkdirSync(directory,{recursive:true,mode:0o700});chmodSync(directory,0o700);let fd;
  try{fd=openSync(path,'wx',0o600);writeFileSync(fd,randomBytes(32));fsyncSync(fd);}catch(error){if(error.code!=='EEXIST')throw Error('Connect encryption key could not be created.');}finally{if(fd!==undefined)closeSync(fd);}
  return key(false);
 }
 return {
  encryptSecret(plain){const iv=randomBytes(12),cipher=createCipheriv('aes-256-gcm',key(true),iv),encrypted=Buffer.concat([cipher.update(plain,'utf8'),cipher.final()]);return 'enc:v1:'+iv.toString('base64url')+':'+cipher.getAuthTag().toString('base64url')+':'+encrypted.toString('base64url');},
  decryptSecret(value){if(typeof value!=='string'||!value.startsWith('enc:v1:'))throw Error('Invalid encrypted Connect state.');const parts=value.slice(7).split(':');if(parts.length!==3)throw Error('Invalid encrypted Connect state.');const [iv,tag,data]=parts.map(part=>Buffer.from(part,'base64url'));if(iv.length!==12||tag.length!==16)throw Error('Invalid encrypted Connect state.');const cipher=createDecipheriv('aes-256-gcm',key(),iv);cipher.setAuthTag(tag);return Buffer.concat([cipher.update(data),cipher.final()]).toString('utf8');}
 };
}
