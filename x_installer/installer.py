import os
import json
import shutil
import requests
from datetime import datetime
from pathlib import Path

# OPTIONS
REPO_URL = os.environ.get("REPO", "https://github.com/Osauhing-X/home-assistant.git")
INTERVAL = int(os.environ.get("INTERVAL", 3600))

# HA config paths
HA_CONFIG = Path("/config")
CUSTOM_COMPONENTS = HA_CONFIG / "custom_components"
PLUGINS_DIR = "plugins"

# Tuleta maintainer GitHubi URL-st
GITHUB_OWNER = REPO_URL.split("github.com/")[1].split("/")[0]

# Logimine
def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

# Lae pluginad GitHubist (ZIP)
def download_plugins():
    url = REPO_URL.replace(".git", "/archive/refs/heads/main.zip")
    log(f"Downloading plugins from {url}")
    r = requests.get(url, stream=True)
    zip_path = "/tmp/plugins.zip"
    with open(zip_path, "wb") as f:
        f.write(r.content)
    return zip_path

# Ekstrakti ainult /plugins kaust
def extract_plugins(zip_path, target_dir):
    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            if f"/{PLUGINS_DIR}/" in member:
                dest_path = Path(target_dir) / "/".join(member.split("/")[2:])
                if member.endswith("/"):
                    dest_path.mkdir(parents=True, exist_ok=True)
                else:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(dest_path, "wb") as f:
                        f.write(zip_ref.read(member))
    log(f"Plugins extracted to {target_dir}")

# Kontrolli ja uuenda ainult sinu repo pluginaid
def update_plugins():
    CUSTOM_COMPONENTS.mkdir(parents=True, exist_ok=True)
    zip_file = download_plugins()
    extract_plugins(zip_file, CUSTOM_COMPONENTS)
    # Iga plugin kausta manifest
    for plugin_path in CUSTOM_COMPONENTS.iterdir():
        manifest_file = plugin_path / "manifest.json"
        if not manifest_file.exists():
            continue
        with open(manifest_file, "r") as f:
            manifest = json.load(f)
        # Lisa maintainer GitHubi user
        if manifest.get("maintainer") != GITHUB_OWNER:
            manifest["maintainer"] = GITHUB_OWNER
            with open(manifest_file, "w") as f:
                json.dump(manifest, f, indent=2)
            log(f"Updated maintainer for {manifest.get('domain')} -> {GITHUB_OWNER}")
    log("Plugin check complete.")

if __name__ == "__main__":
    log("=== Plugin update job started ===")
    update_plugins()
    log("=== Plugin update job finished ===")