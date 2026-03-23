import fs from 'fs';
import path from 'path';
import fetch from 'node-fetch';

const HA_CONFIG = process.env.HA_CONFIG || '/config'; // HA add-on path
const COMPONENTS_PATH = path.join(HA_CONFIG, 'custom_components');
const PLUGINS_PATH = path.join(process.cwd(), 'plugins');

function copyRecursive(src, dest) {
  if (!fs.existsSync(src)) return;
  if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });
  const entries = fs.readdirSync(src, { withFileTypes: true });
  for (let entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) copyRecursive(srcPath, destPath);
    else fs.copyFileSync(srcPath, destPath);
  }
}

async function main() {
  console.log('=== Extaas HA Plugin Installer Add-on ===');

  if (!fs.existsSync(COMPONENTS_PATH)) {
    console.log('custom_components kaust puudub, loome...');
    fs.mkdirSync(COMPONENTS_PATH, { recursive: true });
  }

  // Kopeerime kõik pluginad
  const plugins = fs.readdirSync(PLUGINS_PATH, { withFileTypes: true })
                    .filter(d => d.isDirectory());
  for (let plugin of plugins) {
    const src = path.join(PLUGINS_PATH, plugin.name);
    const dest = path.join(COMPONENTS_PATH, plugin.name);
    copyRecursive(src, dest);
    console.log(`Plugin '${plugin.name}' kopeeritud!`);
  }

  // Optional: restart HA API kaudu
  const HA_URL = process.env.HA_URL;
  const HA_TOKEN = process.env.HA_TOKEN;

  if (HA_URL && HA_TOKEN) {
    console.log('Käivitan HA restarti...');
    try {
      const res = await fetch(`${HA_URL}/api/services/homeassistant/restart`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${HA_TOKEN}`,
          'Content-Type': 'application/json'
        }
      });
      if (res.ok) console.log('HA restart käivitati!');
      else console.log('Viga restartimisel:', res.statusText);
    } catch (e) {
      console.log('Viga:', e.message);
    }
  }

  console.log('Kõik valmis! Pärast restarti ilmuvad entityd HA UI-s.');
}

main();