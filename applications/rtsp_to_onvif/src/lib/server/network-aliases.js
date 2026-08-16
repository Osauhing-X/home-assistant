import { createHash } from 'node:crypto';
import { execFile } from 'node:child_process';
import { chmod, readFile, unlink, writeFile } from 'node:fs/promises';
import os from 'node:os';
import { promisify } from 'node:util';

const exec=promisify(execFile),active=new Map(),dhcpScript='/tmp/x-onvif-udhcpc.sh';
const valid=value=>/^((25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(25[0-5]|2[0-4]\d|1?\d?\d)$/.test(String(value||''));
const run=async(...args)=>exec('ip',args);
const ifaceName=id=>`xov${createHash('sha1').update(id).digest('hex').slice(0,8)}`;
export const virtualMac=id=>{const bytes=createHash('sha256').update(id).digest().subarray(0,6);bytes[0]=(bytes[0]&0xfe)|0x02;return[...bytes].map(value=>value.toString(16).padStart(2,'0')).join(':')};

function physical(host){for(const [name,list] of Object.entries(os.networkInterfaces())){const address=(list||[]).find(item=>item.family==='IPv4'&&item.address===host);if(address)return{name,address}}return null}
const prefix=netmask=>String(netmask||'255.255.255.0').split('.').reduce((sum,value)=>sum+Number(value).toString(2).replace(/0/g,'').length,0);
async function remove(name){try{await run('link','del',name)}catch{}active.delete(name)}

async function dhcp(name){
  const lease=`/tmp/${name}.lease`;await unlink(lease).catch(()=>{});
  await writeFile(dhcpScript,'#!/bin/sh\ncase "$1" in bound|renew) echo "$ip $subnet" > "/tmp/$interface.lease" ;; esac\n');await chmod(dhcpScript,0o755);
  await exec('udhcpc',['-i',name,'-n','-q','-t','5','-T','3','-s',dhcpScript]);
  const [address,mask]=String(await readFile(lease,'utf8')).trim().split(/\s+/);if(!valid(address))throw new Error(`DHCP did not assign an address to ${name}`);
  await run('address','add',`${address}/${prefix(mask)}`,'dev',name);return address;
}

export async function syncAliases(cameras,host){
  const parent=physical(host);if(!parent)throw new Error('Could not find the physical network interface for virtual cameras.');
  const wanted=new Set(cameras.map(camera=>ifaceName(camera.id)));for(const name of [...active.keys()])if(!wanted.has(name))await remove(name);
  const addresses=new Map();
  for(const camera of cameras){
    const name=ifaceName(camera.id),signature=`${camera.ipMode==='static'?'static':'dhcp'}:${camera.virtualIp||''}`,existing=active.get(name);if(existing?.signature===signature){addresses.set(camera.id,existing.address);continue}
    await remove(name);await run('link','add',name,'link',parent.name,'address',virtualMac(camera.uuid||camera.id),'type','macvlan','mode','bridge');await run('link','set',name,'up');
    try{const address=camera.ipMode==='static'?(valid(camera.virtualIp)?camera.virtualIp:null):await dhcp(name);if(!address)throw new Error(`Choose a valid static IP for ${camera.name}.`);if(address===host)throw new Error(`${camera.name} cannot use the X host IP ${host}; choose a separate address.`);if(camera.ipMode==='static')await run('address','add',`${address}/${prefix(parent.address.netmask)}`,'dev',name);active.set(name,{address,signature});addresses.set(camera.id,address);console.log(`[ONVIF network] ${camera.name} ${camera.ipMode==='static'?'static':'DHCP'} ${address} (${name}, ${virtualMac(camera.uuid||camera.id)})`)}catch(error){await remove(name);throw error}
  }
  return addresses;
}

export async function clearAliases(){for(const name of [...active.keys()])await remove(name)}
