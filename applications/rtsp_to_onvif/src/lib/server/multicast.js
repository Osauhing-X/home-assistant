export function joinDiscoveryMulticast(socket,onUnavailable=()=>{}){
 try{socket.addMembership('239.255.255.250');return true;}
 catch{try{socket.close();}catch{}onUnavailable();return false;}
}
