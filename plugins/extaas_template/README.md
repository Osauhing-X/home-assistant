https://my.home-assistant.io/redirect/config_flow_start/?domain=extaas_template

--

http://home.local:8123/config/integrations/integration/extaas_template

Node.js rakendus + mDNS auto-discovery


- Kirje lisamisel tekkib koheselt heartbeat entity (PORT ja IP olemas)
- HA saadab heartbeat kui IP:PORT olemas
- Kui node pole HA-s, kuvatakse Leitud seadmed automaatselt (mDNS auto-discovery)
- Heartbeat näitab True/False, sõltuvalt viimase saadud signaali ajast.
- Dynamic entity’d tekivad Node poolt saadetud võtmete põhjal.
- OptionsFlow/ConfigFlow olemas name, host, port muutmiseks.
- Helper.py kasutatakse korduvfunktsioonide jaoks.

---

- Node rakendus saadab andmed POST-ga /api/extaas_template.
- Kui Node POST ei sisalda mingi objekt key-d siis see kustutatakse.
- Node POST, mis olemas HA-s staatus uuendatkase.




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





























mDNS / SSDP / Zeroconf / UPnP <- aga kas nodejs rakendust ei saaks sama moodi teha siis? siis ei peaks HA aadressi teadam ja alles siis kui link loodud hakkab ta andmed edastama. 
