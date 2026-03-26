https://my.home-assistant.io/redirect/config_flow_start/?domain=extaas_template

--

http://home.local:8123/config/integrations/integration/extaas_template

https://developers.home-assistant.io/docs/network_discovery/

Node.js rakendus + mDNS auto-discovery + Zeroconf

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

✅ mDNS → auto discovery töötab (Zeroconf)
✅ HA loob seadme UI-s
✅ kohe tekib heartbeat sensor
✅ HA pollib /heartbeat → True/False
✅ Node POST → /api/extaas_template
✅ dynamic entity’d tekivad automaatselt
✅ kui key kaob → eemaldatakse store-ist
✅ entity ei kao enne uut POST-i


✅ 1 entry per IP
✅ mitu service’t sama entry all
✅ iga service = eraldi device
✅ heartbeat töötab HA poolt
✅ node EI halda heartbeat’i
✅ dynamic sensorid uuenevad
✅ vanad sensorid kustutatakse


- Heartbeat sensor tekib kohe kirje lisandumisel
- Heartbeat hakkab antud IP:PORT pärima, kui vastus 200/ok siis "true", kui aga mitte siis "false"
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






Grupp (kirje) <- seadme nimi: "taavi-book-13" kindal IP-ga

Iga kirje/grupp on erinev IP

iga seade kirje/grupp sees on erinev port aga sama ip-ga -> tegu on teenus / serveriga

nt:
taavi-book-13 <- (10.10.1.99), (kirje)
- Discord (10.10.1.99:3400) <- heartbeat sensor, muud sensorid ...
- Website (10.10.1.99:5003) <- heartbeat sensor, muud sensorid ...

asus_rog-7 (10.10.1.207)
- Discord (10.10.1.207:7300) <- heartbeat sensor, muud sensorid ...
- Website (10.10.1.207:6601) <- heartbeat sensor, muud sensorid ...

---

realsuses nime järgi ei lisa pingeid ip-sid ega porte:
taavi-book-13
- Discord
- Website


ja igal teenusel on oma heartbeat mida kohtrollib HA. Node ise ei edasta hearbeati. Kui teenus vastab HA-le 200/OK siis heartbeat on tru aag kui mitte siis false.
app.get("/heartbeat", (req, res) => {
  // Heartbeat: TRUE kui server vastab
  res.json({
    ok: true,
    uptime: Math.floor((Date.now() - startTime) / 1000),
    timestamp: Date.now()
  });
});


Node edastab HA-le "/api/extaas_template" andmeid ja nendest teeb sensorid, mille väärtused uuendavada peale igad node edastust.
[{ name: "requests", value: 0, icon: "mdi:network", device_class: "measurement" }, {...}]


kui uus objekt ei sisalda midagi mis eelmises objektis oli siis kustuta see.

Kui node pannakse tööle ja seda veel HA-s ei ole siis esmalt läheb see discovery-sse (leitud) sektsiooni dashboard-l

KIRJE (grupp) = node (IP põhine) <- kood host seade
  ↓
DEVICE (teenus / node) = (PORT põhine) <- sama IP
  ↓
SENSORID
  - heartbeat (HA kontrollib /health)
  - dünaamilised sensorid (nodeData)



HA -> mDNS Zeroconf (auto-discovery), kui seade ilmub siis pealkiri peask olema teenuse nimi nt Discord võ iWebsite ja subpealkiri on nt siis IP. Hetkel on tuvastatud seadmetel sama nimi:
title: Extaas Template
subtitle: X Template

kui vajutab lisa siis küsib kasutaalt nime kohta kas soovib muuta. nagu ta praegult on AGA hetkel on väärtus "taavi-book-13._extaas-node._tcp.local." aga võiks olla "taavi-book-13" koheselt. 


Tee full parantatud kood antud sisu järgi