import { appendLog } from '$lib/server/logger';
import fs from 'fs';
import path from 'path';
import { json } from '@sveltejs/kit';

const LOG_DIR = '/data'; // logide kaust

/** @type {import('./$types').RequestHandler} */
export async function POST({ url }) {
  const name = url.searchParams.get('name');
  const linesCount = parseInt(url.searchParams.get('lines') || '50');

  if (!name) return json({ error: 'Missing name parameter' });

  const logFile = path.join(LOG_DIR, `${name}.log`);
  if (!fs.existsSync(logFile)) {
    // logime ka appendLog-iga
    appendLog(name, 'No log file found');
    return json({ name, lines: [`No log file for ${name}`] });
  }

  try {
    const raw = fs.readFileSync(logFile, 'utf-8');
    let lines = raw.split('\n').filter(Boolean);

    // võtame ainult viimased linesCount rida
    lines = lines.slice(-linesCount);

    // eemaldame prefixi "[<name>] "
    const prefixRegex = new RegExp(`^\\[${name}\\]\\s*`);
    lines = lines.map(line => line.replace(prefixRegex, ''));

    return json({ name, lines });
  } catch (e) {
    appendLog(name, `Error reading log file: ${e.message}`);
    return json({ error: e.message, lines: [] });
  }
}