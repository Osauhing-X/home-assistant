import { json } from '@sveltejs/kit';
import { AUTH_COOKIE, authToken } from '../../../hooks.server.js';

export async function POST({ request, cookies, url }) {
  let input;
  try { input = await request.json(); }
  catch { return json({ error: 'Invalid request.' }, { status: 400 }); }
  if (!process.env.PASSWORD || String(input?.password || '') !== process.env.PASSWORD) {
    return json({ error: 'Invalid password.' }, { status: 401 });
  }
  cookies.set(AUTH_COOKIE, authToken(), {
    path: '/', httpOnly: true, sameSite: 'lax', secure: url.protocol === 'https:', maxAge: 60 * 60 * 24 * 7
  });
  return json({ ok: true });
}
