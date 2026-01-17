#!/usr/bin/env python3
import os

print("Starting Lighttpd ingress UI on port 8099")

conf_path = "/etc/lighttpd/lighttpd.conf"
htdocs = "/var/www/localhost/htdocs"

os.makedirs(htdocs, exist_ok=True)
if not os.path.exists(conf_path):
    with open(conf_path, "w") as f:
        f.write(f"""
server.port = 8099
server.bind = "0.0.0.0"
server.document-root = "{htdocs}"
server.modules = ("mod_accesslog")
index-file.names = ("index.html")
accesslog.filename = "/var/log/lighttpd/access.log"
""")

# Eemaldame vale cp käsu
# os.system(f"cp -r /www/* {htdocs}/")  # <-- see pole enam vajalik

# Käivitame Lighttpd foregroundis
os.system("lighttpd -D -f /etc/lighttpd/lighttpd.conf")
