https://my.home-assistant.io/redirect/config_flow_start/?domain=extaas_template

--

http://home.local:8123/config/integrations/integration/extaas_template

Node.js rakendus + mDNS auto-discovery

translations/en.json
__init__.py
api.py
config_flow.py
options_flow.py
const.py
store.py
coordinator.py
helper.py
manifest.json
sensor.py




- Heartbeat sensor tekib kohe kirje lisandumisel
- Heartbeat hakkab antud IP:PORT pärima, kui vastus 200 siis "true", kui aga mitte siis "false"
- Heartbeat näitab True/False, sõltuvalt viimase saadud signaali ajast.
- Kui node rakendus pole HA-s, kuvatakse see leitud seadmed sektsioonis automaatselt (mDNS auto-discovery)
- Dynamic entities tekivad Node POST põhjal.
- OptionsFlow/ConfigFlow olemas name, host, port muutmiseks.
- Helper.py kasutatakse korduvfunktsioonide jaoks.

---

- Node rakendus saadab andmed POST-ga /api/extaas_template.
- Kui Node POST ei sisalda mingi objekt key-d siis see kustutatakse.
- Node POST, mis olemas HA-s staatus uuendatkase.
- mDNS auto-discovery tehakse NodeJS kliendi kaudu (näiteks bonjour paketiga).



// --- mDNS / Auto-Discovery --- //
const bonjourService = bonjour();
bonjourService.publish({
  name: NODE_NAME,
  type: "extaas-node",
  port: PORT,
  host: HOST,
  txt: {
    integration: INTEGRATION,   // HA domeen
    node_name: NODE_NAME,       // Node nimi, mida saab muuta
    host: HOST,                 // IP, kuhu HA saab ühenduda
    port: PORT,                 // Node port
    model: "Node Client",
    version: "0.0.1",
    capabilities: "heartbeat,sensor,dynamic_entities"
  }
});
























