import { json } from '@sveltejs/kit';
import fs from 'fs';
const STATUS_FILE = '/server/status.json';

export async function GET() {
  if (!fs.existsSync(STATUS_FILE)) return json({});
  const data = JSON.parse(fs.readFileSync(STATUS_FILE));
  return json(data);
}