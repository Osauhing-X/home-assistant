#!/usr/bin/env python3
import os

print("Starting Lighttpd ingress UI on port 8099")

# Loo lighttpd config, kui seda pole
conf_path = "/etc/lighttpd/lighttpd.conf"
if not os.path.exists(conf_path):
    os.makedirs("/var/www/localhost/htdocs", exist_ok=True)
    with open(conf_path, "w") as f:
        f.write("""server.port = 8099
server.bind = "0.0.0.0"
server.document-root = "/var/www/localhost/htdocs"
server.modules = ("mod_accesslog")
index-file.names = ("index.html")
accesslog.filename = "/var/log/lighttpd/access.log"
""")

# Käivitame Lighttpd foregroundis
os.system("lighttpd -D -f /etc/lighttpd/lighttpd.conf")
