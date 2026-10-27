import path from 'node:path';
import {createCameraStore} from './camera-store.js';
const dir=process.env.RTSP_ONVIF_DATA||path.join(process.env.DATA_DIR||path.resolve('.data'),'application-data','rtsp-to-onvif');
const storage=createCameraStore(dir);
export const cameras=storage.cameras,save=storage.save,updateCameras=storage.updateCameras,settings=storage.settings,saveSettings=storage.saveSettings;
export const setCameraDiscovery=(id,enabled)=>updateCameras(all=>{const camera=all.find(item=>item.id===id);if(!camera||(!enabled&&camera.discoveryMode==='off'))return false;camera.discoveryMode=enabled?'on_connect':'off';camera.discoveryEnabled=enabled;camera.discoveryUntil=0;return true;});
export const saveDhcpLeases=addresses=>updateCameras(all=>{let changed=false;for(const camera of all){const address=addresses.get(camera.id);if(camera.ipMode!=='static'&&address&&camera.dhcpIp!==address){camera.dhcpIp=address;changed=true;}}return changed;});