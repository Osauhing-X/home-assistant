import { json } from '@sveltejs/kit';
import fs from 'fs';

const STATUS_FILE = '/server/status.json';

export async function GET() {
  if (!fs.existsSync(STATUS_FILE)) return json({});

  let data = JSON.parse(fs.readFileSync(STATUS_FILE));

  for (const name of Object.keys(data)) {
    const pkgPath = `/server/app_${name}/package.json`;

    try {
      if (fs.existsSync(pkgPath)) {
        const pkg = JSON.parse(fs.readFileSync(pkgPath));
        data[name].version = pkg.version || 'unknown';
      } else {
        data[name].version = 'no package.json';
      }
    } catch (e) {
      data[name].version = 'error';
    }
  }

  return json(data);
}