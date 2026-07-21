import { appendLog } from '$lib/server/logger';
import fs from 'fs';
import { json } from '@sveltejs/kit';

const LOG_DIR = '/data'; // logide kaust

/** @type {import('./$types').RequestHandler} */
export async function POST({ url }) {
  const name = url.searchParams.get('name');
  const requestedLines = Number.parseInt(url.searchParams.get('lines') || '50', 10);
  const linesCount = Number.isFinite(requestedLines)
    ? Math.min(Math.max(requestedLines, 1), 500)
    : 50;

  if (!name) return json({ error: 'Missing name parameter' }, { status: 400 });
  if (!/^[a-zA-Z0-9._-]+$/.test(name)) {
    return json({ error: 'Invalid application name' }, { status: 400 });
  }

  const logFile = `${LOG_DIR}/${name}.log`;
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
    const escapedName = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const prefixRegex = new RegExp(`^\\[${escapedName}\\]\\s*`);
    lines = lines.map(line => line.replace(prefixRegex, ''));

    return json({ name, lines });
  } catch (e) {
    appendLog(name, `Error reading log file: ${e.message}`);
    return json({ error: e.message, lines: [] });
  }
}
