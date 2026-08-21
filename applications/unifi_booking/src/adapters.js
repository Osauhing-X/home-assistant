export class HomeAssistantAdapter {
  constructor({base='http://supervisor/core/api',token=process.env.SUPERVISOR_TOKEN}={}){this.base=base;this.token=token}
  async call(domain,service,data={}){if(!this.token) throw new Error('Home Assistant supervisor token is unavailable'); const r=await fetch(`${this.base}/services/${domain}/${service}`,{method:'POST',headers:{Authorization:`Bearer ${this.token}`,'content-type':'application/json'},body:JSON.stringify(data)}); if(!r.ok) throw new Error(`Home Assistant ${r.status}`); return r.json()}
}

export class UniFiAdapter {
  constructor({base,apiKey,verifyTls=true}={}){this.base=base?.replace(/\/$/,'');this.apiKey=apiKey;this.verifyTls=verifyTls}
  async request(path,init={}){if(!this.base||!this.apiKey) throw new Error('UniFi controller is not configured'); const r=await fetch(`${this.base}${path}`,{...init,headers:{'x-api-key':this.apiKey,'content-type':'application/json',...init.headers}}); if(!r.ok) throw new Error(`UniFi ${r.status}`); return r.status===204?null:r.json()}
  // Access API paths differ by controller generation. Keep provisioning centralized and test against the target controller.
  async listDoors(){return this.request('/proxy/access/api/v1/developer/doors')}
  async provisionCredential(payload){return this.request('/proxy/access/api/v1/developer/credentials',{method:'POST',body:JSON.stringify(payload)})}
  async revokeCredential(id){return this.request(`/proxy/access/api/v1/developer/credentials/${encodeURIComponent(id)}`,{method:'DELETE'})}
}

export class SupabaseAdapter {
  constructor({url,key,accessToken}={}){this.url=url?.replace(/\/$/,'');this.key=key;this.accessToken=accessToken}
  async from(table,{method='GET',query='',body}={}){if(!this.url||!this.key) throw new Error('Supabase is not configured'); const r=await fetch(`${this.url}/rest/v1/${table}${query}`,{method,headers:{apikey:this.key,Authorization:`Bearer ${this.accessToken||this.key}`,'content-type':'application/json',Prefer:'return=representation'},body:body?JSON.stringify(body):undefined}); if(!r.ok) throw new Error(`Supabase ${r.status}: ${await r.text()}`); return r.status===204?null:r.json()}
}
