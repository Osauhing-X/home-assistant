esp32_ble_addon/
│
├─ www/
│   └─ index.html       # Veebiliides
│
├─ server/
│   ├─ __init__.py      # Tühjaks, et server kaust oleks Python package
│   ├─ mqtt_server.py   # MQTT ühendus
│   └─ flask_app.py     # Flask REST API
│
├─ run.sh               # Käivitab Lighttpd + serverid
├─ Dockerfile
└─ config.yaml
